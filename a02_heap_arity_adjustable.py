'''
Authored by Sihyung Lee
'''
import inspect  # to obtain function names in the stack

'''
d-ary indexed minimum heap with the following functions implemented
    (1) dynamically adjustable arity (O)
    (2) bottom-up delete-min (O)
    (3) min caching (O)
'''
class DaryHeapBCD: 
    def __init__(self, max_n, arity_adjustment_policy=0, d_from=2, d_to=2, weight_on_current=0.2):
        assert isinstance(max_n, int) and 1 <= max_n, f"maxN({max_n}), the max # of elements must be an integer >= 1"        
        self.max_n = max_n          # max number of elements
        self.n = 0                  # current number of elements
        self.keys = [None] * max_n  # keys[index]: key with index
        self.heap = [-1] * max_n    # heap[i]: index of key at heap position i
        self.qp = [-1] * max_n      # qp[index]: heap position of the key with index (inverse of heap[])
        
        self.validate_arity(d_from)        
        self.d = d_from        

        # variables required for caching min child index
        self.min_child = [-1] * max_n       # min_child[i]: cached heap position of the smalled child of heap position i
        self.cache_ver = [0] * max_n    # cache_ver[i]: version at which the cache at min_child[i] was computed
        self.parent_ver = [0] * max_n   # parent_ver[i]: increments when a child of i changes key or moves in/out of i's child set
        
        #
        # variables required for dynamic arity adjustment        
        #
        self.arity_adjustment_policy = arity_adjustment_policy
        self.validate_arity(d_to)        
        self.arity_destination = d_to
        self.num_comparions_for_sift_up = 0
        self.num_comparions_for_sift_down = 0       
        
        self.weight_on_current = weight_on_current
        #self.ud_ratio = None
        self.num_comparions_for_sift_up_ema = None
        self.num_comparions_for_sift_down_ema = None        

        #
        # variables required for logging and debugging
        #
        self.num_comparisons = 0
        self.num_operations = 0
        self.num_comparisons_for_arity_adjustment = 0
        self.num_operations_at_arity_change = None
        

    def is_empty(self): return self.n == 0

    def validate_arity(self, arity):
        assert isinstance(arity, int) and 2 <= arity, f"arity({arity}) must be an integer >= 2"

    def validate_index(self, index):
        assert isinstance(index, int) and 0 <= index < self.max_n, f"index({index}) must be an integer between 0 and capacity - 1({self.max_n - 1})"        

    def contains(self, index):      # Is index being used in the heap?
        self.validate_index(index)
        return self.qp[index] != -1

    def size(self): return self.n

    def invalidate_cache(self, i):
        p = self.parent(i)
        if p is not None: self.parent_ver[p] += 1

    def swap(self, i, j):        
        self.heap[i], self.heap[j] = self.heap[j], self.heap[i]
        self.qp[self.heap[i]] = i
        self.qp[self.heap[j]] = j
        self.invalidate_cache(i)
        self.invalidate_cache(j)

    def parent(self, i): return (i - 1) // self.d if i > 0 else None

    def children(self, i): return range(i * self.d + 1, min(i * self.d + self.d + 1, self.size()))    

    def greater(self, i, j): return self.keys[self.heap[i]] > self.keys[self.heap[j]]

    def sift_up(self, i):
        count = 0
        p = self.parent(i)
        while p is not None and self.greater(p, i):
            self.swap(i, p)
            i = p
            count += 1
            p = self.parent(i)
        if p is not None: count += 1
        
        self.num_comparisons += count
        self.num_comparions_for_sift_up += count        
        self.increase_operation_count()

    def sift_down(self, i):
        count = 0
        while 0 < len(self.children(i)):
            min_child_i, count_delta = self.get_min_child(i)
            count += count_delta + 1
            if not self.greater(i, min_child_i): break
            self.swap(i, min_child_i)
            i = min_child_i

        self.num_comparisons += count    
        self.num_comparions_for_sift_down += count        
    
    #
    #   adjust the arity based on observed workload
    #
    def increase_operation_count(self):
        self.num_operations += 1

        if self.arity_adjustment_policy == 0: return    # no arity change        
        elif self.arity_adjustment_policy == -1 and self.num_operations_at_arity_change is None:  # perform a one-time arity change
            #
            # use exponential moving average of U/D ratio to change arity
            #
            if self.num_comparions_for_sift_up_ema is not None and self.num_comparions_for_sift_down_ema is not None:
                if self.num_comparions_for_sift_up_ema / self.num_comparions_for_sift_down_ema < 1:
                    self.change_arity(self.arity_destination)
                    self.num_operations_at_arity_change = self.num_operations

    def insert(self, index, key):
        self.validate_index(index)
        assert not self.contains(index), f"index({index}) is already being used"
        self.n += 1
        self.keys[index] = key
        self.heap[self.n - 1] = index
        self.qp[index] = self.n - 1
        self.invalidate_cache(self.n - 1)
        self.sift_up(self.n - 1)               

    def min_index(self):            # return the index associated with the minimum key
        assert 0 < self.size(), f"heap has no element, so no min index exists"
        return self.heap[0]
    
    def min_key(self):
        assert 0 < self.size(), f"heap has no element, so no min key exists"
        return self.keys[self.heap[0]]
    
    #
    # Floyd's bottom-up heapify that runs in O(n) on average    
    #
    def change_arity(self, new_arity):
        self.validate_arity(new_arity)

        old_arity, old_num_comparisons_for_sift_down = self.d, self.num_comparions_for_sift_down

        self.d = new_arity
        for i in range(1, self.n): self.invalidate_cache(i)

        num_comparisons_before_arity_adjustment = self.num_comparisons
        #
        # The nodes that do not have any child already form a heap, and thus
        #   sift-down all nodes that has at least one child in reverse order
        #
        for i in range((self.n - 2) // self.d, -1, -1):      # the parent of the last element N-1 is at (N-1 - 1) // d
            self.sift_down(i)       # build a heap rooted at i

        self.num_comparisons_for_arity_adjustment = self.num_comparisons - num_comparisons_before_arity_adjustment
        self.num_comparions_for_sift_down = old_num_comparisons_for_sift_down  # do not include the comparions required for arity change in computing the ratio of up/down conparisons

    def get_min_child(self, i):
        #
        #   return the mininum child of node i and cache the results
        #
        count = 0        
        if self.cache_ver[i] != self.parent_ver[i]:     # recompute the cache if it is obsolete
            c = self.children(i)
            count += len(c) - 1
            min_child_i = None
            for child_i in c: 
                if min_child_i is None or self.greater(min_child_i, child_i): min_child_i = child_i  
            self.min_child[i] = min_child_i
            self.cache_ver[i] = self.parent_ver[i]
        return self.min_child[i], count               # return the cache

    def delete_min(self): 
        #
        #   delete_min with bottom-up sift-down and min-caching
        #
        assert 0 < self.size(), "no element exists to delete"
        min_index = self.heap[0]
        min_key = self.keys[min_index]
        
        # identify the min-child path from root to a leaf
        count = 0
        i = 0
        path = [0]
        while 0 < len(self.children(i)):
            min_child_i, count_delta = self.get_min_child(i)
            path.append(min_child_i)
            count += count_delta            
            i = min_child_i

        # assuming that the last element moves to the bottom of the path,
        # figure out how far it is going to sift up - this corresponds to path[j]
        j = len(path) - 1
        while 0 < j:            
            count += 1
            if self.greater(path[j], self.n - 1): j -= 1 # this element should stay as it is
            else: break

        # move up the min children from path[0] to path[j-1]
        for k in range(0, j): self.swap(path[k], path[k + 1])
        
        # place the last element at path[j]
        if path[j] < self.n - 1:
            self.swap(path[j], self.n - 1)            
        self.n -= 1        
        self.keys[min_index] = None
        self.heap[self.n] = -1
        self.qp[min_index] = -1

        self.num_comparisons += count    
        self.num_comparions_for_sift_down += count        

        if 0 < self.num_comparions_for_sift_down:
            #
            # compute the ema (exponential moving average) of the number of sift-ups and sift-downs
            #
            if self.num_comparions_for_sift_up_ema is None: self.num_comparions_for_sift_up_ema = self.num_comparions_for_sift_up
            else: self.num_comparions_for_sift_up_ema = self.weight_on_current * self.num_comparions_for_sift_up + (1 - self.weight_on_current) * self.num_comparions_for_sift_up_ema

            if self.num_comparions_for_sift_down_ema is None: self.num_comparions_for_sift_down_ema = self.num_comparions_for_sift_down
            else: self.num_comparions_for_sift_down_ema = self.weight_on_current * self.num_comparions_for_sift_down + (1 - self.weight_on_current) * self.num_comparions_for_sift_down_ema

            self.num_comparions_for_sift_up, self.num_comparions_for_sift_down = 0, 0

        self.increase_operation_count()

        return min_key, min_index

    def key_of(self, index):
        self.validate_index(index)
        assert self.contains(index), f"no key exists with index({index})"
        return self.keys[index]
    
    def decrease_key(self, index, key):
        self.validate_index(index)
        assert self.contains(index), f"no key exists with index({index})"
        assert key < self.keys[index], f"to call decrease_key(), the new key({key}) must be less than the existing key({self.keys[index]})"
        self.keys[index] = key
        self.invalidate_cache(self.qp[index])
        self.sift_up(self.qp[index])

    def __str__(self):
        result = []
        i, num_elements_on_same_level = 0, 1
        while i < self.size():
            for j in range(i, min(i + num_elements_on_same_level, self.size())): result.append(str(self.keys[self.heap[j]]))
            result.append('\n')
            i += num_elements_on_same_level
            num_elements_on_same_level *= self.d
        return ' '.join(result)
        

if __name__ == "__main__":
    pass