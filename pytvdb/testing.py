data = [
    { 'id': 0, 'attr1': True, 'attr2': False },
    { 'id': 1, 'attr1': False, 'attr2': True },
    { 'id': 2, 'attr1': False, 'attr2': False },
    { 'id': 3, 'attr1': True, 'attr2': True }
]

class MyClass(object):
    def __init__(self, data):
        self.id = data['id']
        self.attr1 = data['attr1']
        self.attr2 = data['attr2']

class MyList(list):
    
    def __init__(self, data):
        self.condition1 = True
        self.condition2 = True

        for content in data:
            self.append(MyClass(content))

    def __iter__(self):
        return (self[i] for i in range(len(self)) 
            if ((self.condition1 or self[i].attr1) and
                (self.condition2 or self[i].attr2)))

my_list = MyList(data)
for item in my_list:
    print 'id', item.id, 'attr1', item.attr1, 'attr2', item.attr2
# >> id 0 attr1 True attr2 False
# >> id 1 attr1 False attr2 True
# >> id 2 attr1 False attr2 False
# >> id 3 attr1 True attr2 True

my_list.condition1 = False
# # print my_list.condition1
# # Now it should list only the instances of MyClass that has the attr1 set to False
for item in my_list:
    print 'id', item.id, 'attr1', item.attr1, 'attr2', item.attr2
# >> id 1 attr1 False attr2 True
# >> id 2 attr1 False attr2 False