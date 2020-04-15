from maya import cmds
from maya.api import OpenMaya


def to_dag_path(m_obj):
    if m_obj.hasFn(OpenMaya.MFn.kDagNode):
        m_dag_path = OpenMaya.MDagPath.getAPathTo(m_obj)
        return m_dag_path


def to_object(node_name):
    """ Get the API MObject given the name of an existing node """
    sel = OpenMaya.MSelectionList()
    sel.add(node_name)
    obj = sel.getDependNode(0)
    return obj


def to_dag_path_from_node(node_name):
    node = to_object(node_name)
    return to_dag_path(node)


def get_children(dag_path, num_child, selection_types=None, recursive=True):
    """
    This is a generator to be used to iterate over the
    current dag_path and give all children with the OpenMaya API.

    Args:
        dag_path (OpenMaya.MDagPath): The dag_path where we want children.
        num_child (int): Number of children.
        selection_types (list): list of OpenMaya.MFn.Type
        recursive (bool): if True, get children of children of....

    Returns:
       list (OpenMaya.MDagPath): The DAG path of the Maya
                                 object that is the current iteration.
    """
    if selection_types is None:
        selection_types = []
    nodes = []
    for i in xrange(num_child):
        child = dag_path.child(i)
        dag_path_child = OpenMaya.MDagPath.getAPathTo(child)
        num_child_of_child = dag_path_child.childCount()
        if num_child_of_child != 0 and recursive:
            for my_child in get_children(dag_path_child, num_child_of_child):
                if my_child in nodes:
                    continue
                if selection_types:
                    for selection_type in selection_types:
                        if my_child.apiType() == selection_type:
                            nodes.append(my_child)
                            break
                else:
                    nodes.append(my_child)
        if selection_types:
            for selection_type in selection_types:
                if dag_path_child.apiType() == selection_type:
                    nodes.append(dag_path_child)
        else:
            nodes.append(dag_path_child)
    return nodes


def create_rest_position_vertex_color_set_hierarchy(
        top_nodes, space=OpenMaya.MSpace.kWorld):
    """
    Create color set to a list of nodes

    Args:
        top_nodes (list): list of string of top_nodes

    Returns:

    """
    mdg = OpenMaya.MDGModifier()
    for node in top_nodes:
        dag_path = to_dag_path_from_node(node)
        list_children = get_children(
            dag_path,
            dag_path.childCount(),
            selection_types=[OpenMaya.MFn.kMesh])
        for child in list_children:
            fn_mesh = OpenMaya.MFnMesh(child)
            points = fn_mesh.getPoints(space)
            create_vertex_color_set(
                fn_mesh, "Rest_Position", points, mdg=mdg)
    mdg.doIt()


def create_vertex_color_set(mesh_fn, color_set_name, vertex_colors, mdg):
    """
    Create color set
    """
    mesh_name = mesh_fn.fullPathName()
    vert_ids = xrange(len(vertex_colors))
    colarray = OpenMaya.MColorArray(map(OpenMaya.MColor, vertex_colors))

    current_color_sets = mesh_fn.getColorSetNames()

    if color_set_name in current_color_sets:
        cmds.polyColorSet(mesh_name, delete=True, colorSet=color_set_name)

    clr_vertex_name = "{}.colorPerVertex".format(mesh_name)
    if cmds.objExists(clr_vertex_name):
        cmds.setAttr(clr_vertex_name, lock=False, keyable=True)

    vertex_name = "{}.vertexColor".format(mesh_name)
    if cmds.objExists(vertex_name):
        cmds.setAttr(vertex_name, lock=False, keyable=True)

    mesh_fn.createColorSet(
        color_set_name, False, rep=OpenMaya.MFnMesh.kRGB, modifier=mdg)

    mesh_fn.setCurrentColorSetName(color_set_name, modifier=mdg)
    mesh_fn.setVertexColors(colarray, vert_ids, modifier=mdg)


def execute():
    # get current selection
    sel = cmds.ls(selection=True)

    if not sel:
        raise RuntimeError("Nothing selected!")

    # write positions
    create_rest_position_vertex_color_set_hierarchy(sel)
