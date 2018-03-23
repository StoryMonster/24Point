import copy

def try_add(nums, num1, num2):
    num = num1 + num2
    if len(nums) == 0:
        return 24 - 0.000001 <= num <= 24 + 0.000001
    else:
        new_nums = copy.deepcopy(nums)
        new_nums.append(num)
        return calc_whether_get_24(new_nums)

def try_minus(nums, num1, num2):
    num = abs(num1 - num2)
    if len(nums) == 0:
        return 24 - 0.000001 <= num <= 24 + 0.000001
    else:
        new_nums = copy.deepcopy(nums)
        new_nums.append(num)
        return calc_whether_get_24(new_nums)

def try_times(nums, num1, num2):
    num = num1 * num2
    if len(nums) == 0:
        return 24 - 0.000001 <= num <= 24 + 0.000001
    else:
        new_nums = copy.deepcopy(nums)
        new_nums.append(num)
        return calc_whether_get_24(new_nums)

def try_dev(nums, num1, num2):
    if len(nums) == 0:
    	if  -0.000001 <= num1 <= 0.000001 or -0.000001 <= num2 <= 0.000001:
    		return False
        return (24 - 0.000001 <= num1 * 1.0 / num2 <= 24 + 0.000001) or (24 - 0.000001 <= num2 * 1.0 / num1 <= 24 + 0.000001)
    else:
        new_nums = copy.deepcopy(nums)
        if  -0.000001 <= num1 <= 0.000001 or -0.000001 <= num2 <= 0.000001:
            new_nums.append(0)
            return calc_whether_get_24(new_nums)
        else:
            new_nums.append(num1 * 1.0 / num2)
            if not calc_whether_get_24(new_nums):
                new_nums.pop()
                new_nums.append(num2 * 1.0 / num1)
                return calc_whether_get_24(new_nums)
            return False

def calc_whether_get_24(nums):
    amount = len(nums)
    for i in range(0, amount - 1):
        for j in range(i+1, amount):
            num1 = nums[i]
            num2 = nums[j]
            new_nums = copy.deepcopy(nums)
            new_nums.pop(j)
            new_nums.pop(i)
            if try_add(new_nums, num1, num2) or try_minus(new_nums, num1, num2) \
                or try_times(new_nums, num1, num2) or try_dev(new_nums, num1, num2):
                return True
    return False
