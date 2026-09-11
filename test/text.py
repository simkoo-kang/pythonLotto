
import copy


lists = []
lists.append([0,1])
lists.append([1,1])
lists.append([2,1])
lists.append([3,1])

if [0,1] in lists:
    print("exist")
else:
    print("not exist")


if (0,1) in lists:
    print("exist")
else:
    print("not exist")

lists.sort()
print(lists)

copys = lists.copy()
deeps = copy.deepcopy(lists)

copys.reverse()
print(lists)
print(copys)
print(deeps)
