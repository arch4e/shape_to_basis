bl_info = {
    "name": "Shape to Basis",
    "author": "ゆづりん (yuzurin)",
    "version": (1, 1, 0),
    "blender": (3, 40, 0),
    "location": "View3D > Sidebar",
    "description": "Revers the 1 and 0 of the shapekey",
    "warning": "",
    "doc_url": "",
    "category": "Object",
}

import bpy

class DATA_PT_shape_keys(bpy.types.Panel):
    bl_label = "Shape to Basis"
    bl_idname = "OBJECT_PT_custom_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "S2B"

    @classmethod
    def poll(cls, context):
        # 選択したオブジェクトにシェイプキーが2つ以上ある場合のみパネルを表示
        return (context.object is not None and
                context.object.type == 'MESH' and
                context.object.data.shape_keys is not None and
                len(context.object.data.shape_keys.key_blocks) >= 2)

    def draw(self, context):
        layout = self.layout

        ob = context.object
        key = ob.data.shape_keys
        kb = ob.active_shape_key

        enable_edit = ob.mode != 'EDIT'
        enable_edit_value = False
        enable_pin = False

        if enable_edit or (ob.use_shape_key_edit_mode and ob.type == 'MESH'):
            enable_pin = True
            if ob.show_only_shape_key is False:
                enable_edit_value = True

        row = layout.row()

        rows = 3
        if kb:
            rows = 5

        row.template_list("MESH_UL_shape_keys", "", key, "key_blocks", ob, "active_shape_key_index", rows=rows)

        col = row.column(align=True)

            # シェイプキーの追加削除
        col.operator("object.shape_key_add", icon='ADD', text="").from_mix = False
        col.operator("object.shape_key_remove", icon='REMOVE', text="").all = False

        col.separator()

            # シェイプキーメニュー
        col.menu("MESH_MT_shape_key_context_menu", icon='DOWNARROW_HLT', text="")

            # シェイプキーの上下
        if kb:
            col.separator()

            sub = col.column(align=True)
            sub.operator("object.shape_key_move", icon='TRIA_UP', text="").type = 'UP'
            sub.operator("object.shape_key_move", icon='TRIA_DOWN', text="").type = 'DOWN'
            
        row = layout.row()
    
            # S2Bボタンの追加
        row = layout.row()
        if bpy.context.object.active_shape_key_index == 0:
            row.enabled = False

        row.operator("object.s2b_operator", icon = 'FILE_REFRESH')


#            split = layout.split(factor=0.4)
#            row = split.row()
#            row.enabled = enable_edit
#            row.prop(key, "use_relative")

#            row = split.row()
#            row.alignment = 'RIGHT'

#            sub = row.row(align=True)
#            sub.label()  # XXX, for alignment only
#            subsub = sub.row(align=True)
#            subsub.active = enable_pin
#            subsub.prop(ob, "show_only_shape_key", text="")
#            sub.prop(ob, "use_shape_key_edit_mode", text="")

#            sub = row.row()
#            if key.use_relative:
#                sub.operator("object.shape_key_clear", icon='X', text="")
#            else:
#                sub.operator("object.shape_key_retime", icon='RECOVER_LAST', text="")

#            layout.use_property_split = True
#            if key.use_relative:
#                if ob.active_shape_key_index != 0:
#                    row = layout.row()
#                    row.active = enable_edit_value
#                    row.prop(kb, "value")

#                    col = layout.column()
#                    sub.active = enable_edit_value
#                    sub = col.column(align=True)
#                    sub.prop(kb, "slider_min", text="Range Min")
#                    sub.prop(kb, "slider_max", text="Max")

#                    col.prop_search(kb, "vertex_group", ob, "vertex_groups", text="Vertex Group")
#                    col.prop_search(kb, "relative_key", key, "key_blocks", text="Relative To")

#            else:
#                layout.prop(kb, "interpolation")
#                row = layout.column()
#                row.active = enable_edit_value
#                row.prop(key, "eval_time")

#        layout.prop(ob, "add_rest_position_attribute")

class S2bOperator(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.s2b_operator"
    bl_label = "Shape to Basis"


    def execute(self, context):
       #オブジェクトモードにする
        if bpy.context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')


        # アクティブなオブジェクトとシェイプキーを取得する
        obj = bpy.context.active_object
        shape_key = obj.active_shape_key

        # アクティブなシェイプキーの名前を取得する
        active_shape_key_name = bpy.context.object.active_shape_key.name
        
         # シェイプキーの数を取得する
        shape_key_count = len(obj.data.shape_keys.key_blocks)

        # 選択したシェイプキーのインデックスを取得する
        selected_shape_key_index = obj.active_shape_key_index

        #一旦全てのシェイプキーの値を0にする
        bpy.ops.object.shape_key_clear()


        if shape_key:
            # 選択したシェイプキーの最小値を-1にする
            min_value = shape_key.slider_min
            shape_key.slider_min = -1
            
            # 選択したシェイプキーの値を-1にする
            shape_key.value = -1
            
            # 仮のシェイプキーの作成
            tent_shape_key = obj.shape_key_add(name="Tentative Shape Key", from_mix=True)
            
            # 選択したシェイプキーと仮のシェイプキーの値を1にする
            tent_shape_key.value = 1
            shape_key.value = 1


        # 選択したシェイプキーをBasisの1つ下まで移動させる
        while bpy.context.object.active_shape_key_index > 0:
            bpy.ops.object.shape_key_move(type='UP')
            if bpy.context.object.active_shape_key_index == 0:
                break


        # Basisのindexを指定し、削除する
        bpy.context.object.active_shape_key_index = 1
        bpy.ops.object.shape_key_remove(all=False)

        #仮のシェイプキーを0.5にしたものを作成する
        tent_shape_key.value = 0.5

        # 新しいシェイプキーの作成
        New_shape_key = obj.shape_key_add(name="New Shape key", from_mix=True)

        # 仮のシェイプキーをアクティブにする
        bpy.context.object.active_shape_key_index = len(obj.data.shape_keys.key_blocks) - 2

        #仮のシェイプキーを削除する
        bpy.ops.object.shape_key_remove(all=False)



        # シェイプキーインデックスを1に設定
        obj.active_shape_key_index = 1

        while obj.active_shape_key_index < len(obj.data.shape_keys.key_blocks) - 1:
            #編集モードに入る
            bpy.ops.object.editmode_toggle()

            # 全選択する
            bpy.ops.mesh.select_all(action='SELECT')

            # 選択したシェイプキーに新しいシェイプキーを-1でブレンド
            bpy.ops.mesh.blend_from_shape(shape='New Shape key', blend=-1)

            #編集モードに入る
            bpy.ops.object.editmode_toggle()

            # 次のシェイプキーをアクティブにする
            obj.active_shape_key_index += 1
            

        # 入れ替えたシェイプキーの名前をBasisにする
        bpy.context.object.active_shape_key_index = 0
        bpy.context.object.active_shape_key.name = "Basis"

        # 0と1を反転させたシェイプキーの名前を元の名前にする
        bpy.context.object.active_shape_key_index = len(obj.data.shape_keys.key_blocks) - 1
        bpy.context.object.active_shape_key.name = active_shape_key_name
        
        # シェイプキーを元の場所に戻す
        while bpy.context.object.active_shape_key_index > selected_shape_key_index:
            bpy.ops.object.shape_key_move(type='UP')
            if bpy.context.object.active_shape_key_index == selected_shape_key_index:
                break
            
        return { 'FINISHED' }

def register():
    bpy.utils.register_class(DATA_PT_shape_keys)
    bpy.utils.register_class(S2bOperator)

# シェイプキーパネルを削除
def unregister():
    bpy.utils.unregister_class(DATA_PT_shape_keys)
    bpy.utils.unregister_class(S2bOperator)

if __name__ == "__main__":
    register()
