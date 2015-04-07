# Copyright (C) 2015 OLogN Technologies AG
#
# This source file is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License version 2
# as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

from node import Node

def visit_node(visitor, node):
    '''
    Dynamic version of node visitor
    Trivial implementation 
    '''
    assert isinstance(node, Node)
    getattr(visitor, 'visit_' + type(node).__name__)()


def walk_node_childs(walker, node):
    '''
    Dynamic version of node walker
    Trivial implementation
    '''
    assert isinstance(node, Node)
    names = dir(node)
    for current in names:
        if(current.startswith('child_')):
            ch = getattr(node, current)
            walker.walk_node(ch)
        elif(current.startswith('childs_')):
            chs = getattr(node, current)
            for ch in chs:
                walker.walk_node(ch)
                

class NodeWalker(object):
    pass

class NodeVisitor(object):
    pass


def check_all_nodes_reachables(compiler, root):
    '''
    This function walks a full syntax tree and checks that all nodes are reachable by walking
    Is used as a self check to verify on common issues of the tree structure 
    '''
    walker = CheckReachableWalker(compiler.removed_nodes, compiler.next_node_id)
    walker.walk_node(root)
    walker.finish()

class CheckReachableWalker(NodeWalker):
    '''
    Walker class that will check that every node id is reached in a full tree walk
    Used for consistency check
    '''
    def __init__(self, removed_nodes, next_node_id):
        '''
        Constructor
        '''
        self.dones = []
        self.parents = []
        self.removed_nodes = removed_nodes
        self.next_node_id = next_node_id

    def walk_node(self, node):
        assert node
        if len(self.parents) != 0:
            assert self.parents[-1] == node.parent

        self.dones.append(node.node_id)

        self.parents.append(node)
        walk_node_childs(self, node)
        self.parents.pop()

    def finish(self):
        self.dones += self.removed_nodes
        self.dones.sort()
        expected = 0
        for i in self.dones:
            if self.dones[i] == expected:
                expected += 1
            elif self.dones[i] == expected - 1:
                print 'Node %i has been reached again' % self.dones[i]
            elif self.dones[i] > expected:
                print 'Node range %i to %i has not been reached' % (expected, self.dones[i] - 1)
                expected = self.dones[i] + 1
            else:
                assert False
        
        if expected < self.next_node_id:
            print 'Node range %i to %i has not been reached' % (expected, self.next_node_id - 1)
        elif expected > self.next_node_id:
            assert False
            

def dump_tree(node):
    '''
    This function walks a full syntax tree and checks that all nodes are reachable by walking
    Is used as a self check to verify on common issues of the tree structure 
    '''
    walker = DumpTreeWalker()
    walker.walk_node(node)
    return walker.result

class DumpTreeWalker(NodeWalker):
    '''
    Walker class that will dump  that every node id is reached in a full tree walk
    Used for consistency check
    '''
    def __init__(self):
        '''
        Constructor
        '''
        self.result = []
        self.index = 0

    def walk_node(self, node):
        ctx_attrs = ''
        names = dir(node)
        for current in names:
            if(current.startswith('ctx_')):
                ctx_attrs += " %s='%s'" % (current[4:], getattr(node, current).getText())

        s = '+-' * self.index + type(node).__name__ + ctx_attrs
        self.result.append(s)
        self.index += 1
        walk_node_childs(self, node)
        self.index -= 1

            
