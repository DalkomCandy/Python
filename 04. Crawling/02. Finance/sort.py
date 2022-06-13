def insertion_sort(arr, count = 0):
    for end in range(1, len(arr)):
        for i in range(end, 0, -1):
            if arr[i - 1] > arr[i]:
                arr[i - 1], arr[i] = arr[i], arr[i - 1]
            count += 1
    print(arr)
    print("복잡도 : ", count)
            
            
    
    
arr = [1,2,3,4,5,6,7,8]
insertion_sort(arr)