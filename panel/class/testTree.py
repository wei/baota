#coding: utf-8

#------------------------------
# 二叉树算法
#------------------------------

#节点类
class Node(object):
    def __init__(self, elem=-1, lchild=None, rchild=None):
        self.elem = elem
        self.lchild = lchild
        self.rchild = rchild

#树类
class Tree(object):
    def __init__(self):
        self.root = Node()

    #为树加入节点
    def add(self, elem):
        node = Node(elem)
        if self.root.elem == -1:
            self.root = node
        else:                     
            myQueue = []
            treeNode = self.root
            myQueue.append(treeNode)
            while myQueue:
                treeNode = myQueue.pop(0)
                if treeNode.lchild == None:
                    treeNode.lchild = node
                    return
                elif treeNode.rchild == None:
                    treeNode.rchild = node
                    return
                else:
                    myQueue.append(treeNode.lchild)
                    myQueue.append(treeNode.rchild)

    #利用递归实现树的先序遍历
    def front_digui(self, root):
        if root == None:
            return
        root.elem
        self.front_digui(root.lchild)
        self.front_digui(root.rchild)

    #利用递归实现树的中序遍历
    def middle_digui(self, root):
        if root == None:
            return
        self.middle_digui(root.lchild)
        root.elem
        self.middle_digui(root.rchild)

    #利用递归实现树的后序遍历
    def later_digui(self, root):
        if root == None:
            return
        self.later_digui(root.lchild)
        self.later_digui(root.rchild)
        root.elem

    #利用堆栈实现树的先序遍历
    def front_stack(self, root):
        if root == None:
            return
        myStack = []
        node = root
        while node or myStack:
            while node:                    
                node.elem
                myStack.append(node)
                node = node.lchild
            node = myStack.pop()            
            node = node.rchild                  

    #利用堆栈实现树的中序遍历
    def middle_stack(self, root):
        if root == None:
            return
        myStack = []
        node = root
        while node or myStack:
            while node:                    
                myStack.append(node)
                node = node.lchild
            node = myStack.pop()           
            node.elem
            node = node.rchild                 

    #利用堆栈实现树的后序遍历
    def later_stack(self, root):
        if root == None:
            return
        myStack1 = []
        myStack2 = []
        node = root
        myStack1.append(node)
        while myStack1:                   
            node = myStack1.pop()
            if node.lchild:
                myStack1.append(node.lchild)
            if node.rchild:
                myStack1.append(node.rchild)
            myStack2.append(node)
        while myStack2:                        
            myStack2.pop().elem,

    #利用队列实现树的层次遍历
    def level_queue(self, root):
        if root == None:
            return
        myQueue = []
        node = root
        myQueue.append(node)
        while myQueue:
            node = myQueue.pop(0)
            node.elem
            if node.lchild != None:
                myQueue.append(node.lchild)
            if node.rchild != None:
                myQueue.append(node.rchild)
                
if __name__ == '__main__':
    import time
        
    start = time.time();
    elems = range(5000)             #生成树节点
    tree = Tree()                   #新建一个树对象
    for elem in elems:                  
        tree.add(elem)              #逐个加入树的节点

    tree.level_queue(tree.root)
    tree.front_digui(tree.root)
    tree.middle_digui(tree.root)
    tree.later_digui(tree.root)
    tree.front_stack(tree.root)
    tree.middle_stack(tree.root)
    tree.later_stack(tree.root)
    
    end = time.time();
    usetime = end - start;
    print usetime;
