import random

PROBLEMS = {
    "two_sum": {
        "id": "two_sum",
        "title": "Two Sum",
        "difficulty": "Easy",
        "track": ["google", "meta", "amazon", "general"],
        "category": "Arrays & Hashing",
        "html": '''<h2 class="problemTitle">Two Sum</h2>
<div class="problemText">
    <p>Given an array of integers <span class="codeBlock">nums</span> and an integer <span class="codeBlock">target</span>, return indices of the two numbers such that they add up to <span class="codeBlock">target</span>.</p>
    <p>You may assume that each input would have <strong>exactly one solution</strong>, and you may not use the same element twice.</p>
    <p>You can return the answer in any order.</p>
    <h3>Example 1:</h3>
    <div class="sampleBox">nums = [2,7,11,15], target = 9<br><strong>Output:</strong> [0,1]</div>
    <h3>Example 2:</h3>
    <div class="sampleBox">nums = [3,2,4], target = 6<br><strong>Output:</strong> [1,2]</div>
    <h3>Constraints:</h3>
    <ul>
        <li>2 &le; nums.length &le; 10<sup>4</sup></li>
        <li>-10<sup>9</sup> &le; nums[i] &le; 10<sup>9</sup></li>
        <li>-10<sup>9</sup> &le; target &le; 10<sup>9</sup></li>
    </ul>
</div>''',
        "starter_code": {
            "python": "class Solution:\n    def twoSum(self, nums: list[int], target: int) -> list[int]:\n        # Write your solution here\n        return []",
            "cpp": "#include <bits/stdc++.h>\nusing namespace std;\n\nclass Solution {\npublic:\n    vector<int> twoSum(vector<int>& nums, int target) {\n        // Write your solution here\n        return {};\n    }\n};",
            "java": "import java.util.*;\n\nclass Solution {\n    public int[] twoSum(int[] nums, int target) {\n        // Write your solution here\n        return new int[]{};\n    }\n}"
        },
        "sample_test_cases": [
            {
                "name": "Example 1",
                "input": '{"nums": [2, 7, 11, 15], "target": 9}',
                "input_display": "nums = [2, 7, 11, 15], target = 9",
                "expected_output": "[0, 1]"
            },
            {
                "name": "Example 2",
                "input": '{"nums": [3, 2, 4], "target": 6}',
                "input_display": "nums = [3, 2, 4], target = 6",
                "expected_output": "[1, 2]"
            }
        ],
        "hidden_test_cases": [
            {
                "name": "Negative values",
                "input": '{"nums": [-3, 4, 3, 90], "target": 0}',
                "input_display": "nums = [-3, 4, 3, 90], target = 0",
                "expected_output": "[0, 2]"
            },
            {
                "name": "Duplicates",
                "input": '{"nums": [3, 3], "target": 6}',
                "input_display": "nums = [3, 3], target = 6",
                "expected_output": "[0, 1]"
            }
        ]
    },
    "merge_intervals": {
        "id": "merge_intervals",
        "title": "Merge Intervals",
        "difficulty": "Medium",
        "track": ["google", "meta", "amazon", "general"],
        "category": "Intervals & Sorting",
        "html": '''<h2 class="problemTitle">Merge Intervals</h2>
<div class="problemText">
    <p>Given an array of <span class="codeBlock">intervals</span> where <span class="codeBlock">intervals[i] = [start_i, end_i]</span>, merge all overlapping intervals, and return an array of the non-overlapping intervals that cover all the intervals in the input.</p>
    <h3>Example 1:</h3>
    <div class="sampleBox">intervals = [[1,3],[2,6],[8,10],[15,18]]<br><strong>Output:</strong> [[1,6],[8,10],[15,18]]</div>
    <h3>Example 2:</h3>
    <div class="sampleBox">intervals = [[1,4],[4,5]]<br><strong>Output:</strong> [[1,5]]</div>
    <h3>Constraints:</h3>
    <ul>
        <li>1 &le; intervals.length &le; 10<sup>4</sup></li>
        <li>intervals[i].length == 2</li>
        <li>0 &le; start_i &le; end_i &le; 10<sup>4</sup></li>
    </ul>
</div>''',
        "starter_code": {
            "python": "class Solution:\n    def merge(self, intervals: list[list[int]]) -> list[list[int]]:\n        # Write your solution here\n        return []",
            "cpp": "#include <bits/stdc++.h>\nusing namespace std;\n\nclass Solution {\npublic:\n    vector<vector<int>> merge(vector<vector<int>>& intervals) {\n        // Write your solution here\n        return {};\n    }\n};",
            "java": "import java.util.*;\n\nclass Solution {\n    public int[][] merge(int[][] intervals) {\n        // Write your solution here\n        return new int[][]{};\n    }\n}"
        },
        "sample_test_cases": [
            {
                "name": "Example 1",
                "input": '{"intervals": [[1, 3], [2, 6], [8, 10], [15, 18]]}',
                "input_display": "intervals = [[1,3],[2,6],[8,10],[15,18]]",
                "expected_output": "[[1, 6], [8, 10], [15, 18]]"
            },
            {
                "name": "Example 2",
                "input": '{"intervals": [[1, 4], [4, 5]]}',
                "input_display": "intervals = [[1,4],[4,5]]",
                "expected_output": "[[1, 5]]"
            }
        ],
        "hidden_test_cases": [
            {
                "name": "Fully Enclosed",
                "input": '{"intervals": [[1, 10], [2, 3], [4, 5], [6, 7]]}',
                "input_display": "intervals = [[1,10],[2,3],[4,5],[6,7]]",
                "expected_output": "[[1, 10]]"
            }
        ]
    },
    "longest_substring": {
        "id": "longest_substring",
        "title": "Longest Substring Without Repeating Characters",
        "difficulty": "Medium",
        "track": ["google", "meta", "general"],
        "category": "Sliding Window",
        "html": '''<h2 class="problemTitle">Longest Substring Without Repeating Characters</h2>
<div class="problemText">
    <p>Given a string <span class="codeBlock">s</span>, find the length of the <strong>longest substring</strong> without repeating characters.</p>
    <h3>Example 1:</h3>
    <div class="sampleBox">s = "abcabcbb"<br><strong>Output:</strong> 3<br>Explanation: The answer is "abc", with the length of 3.</div>
    <h3>Example 2:</h3>
    <div class="sampleBox">s = "bbbbb"<br><strong>Output:</strong> 1<br>Explanation: The answer is "b", with the length of 1.</div>
</div>''',
        "starter_code": {
            "python": "class Solution:\n    def lengthOfLongestSubstring(self, s: str) -> int:\n        # Write your solution here\n        return 0",
            "cpp": "#include <bits/stdc++.h>\nusing namespace std;\n\nclass Solution {\npublic:\n    int lengthOfLongestSubstring(string s) {\n        // Write your solution here\n        return 0;\n    }\n};",
            "java": "import java.util.*;\n\nclass Solution {\n    public int lengthOfLongestSubstring(String s) {\n        // Write your solution here\n        return 0;\n    }\n}"
        },
        "sample_test_cases": [
            {
                "name": "Example 1",
                "input": '{"s": "abcabcbb"}',
                "input_display": 's = "abcabcbb"',
                "expected_output": "3"
            },
            {
                "name": "Example 2",
                "input": '{"s": "bbbbb"}',
                "input_display": 's = "bbbbb"',
                "expected_output": "1"
            }
        ],
        "hidden_test_cases": [
            {
                "name": "Empty string",
                "input": '{"s": ""}',
                "input_display": 's = ""',
                "expected_output": "0"
            },
            {
                "name": "With special chars & spaces",
                "input": '{"s": "pwwkew"}',
                "input_display": 's = "pwwkew"',
                "expected_output": "3"
            }
        ]
    },
    "stable_subarrays": {
        "id": "stable_subarrays",
        "title": "Stable Subarrays With Equal Boundary",
        "difficulty": "Medium",
        "track": ["amazon", "google", "general"],
        "category": "Prefix Sums",
        "html": '''<h2 class="problemTitle">Stable Subarrays With Equal Boundary</h2>
<div class="problemText">
    <p>You are given an integer array <span class="codeBlock">capacity</span>.</p>
    <p>A subarray is considered <strong>stable</strong> if:</p>
    <ul>
        <li>Its length is at least <span class="codeBlock">3</span>, and</li>
        <li>The <strong>first</strong> and <strong>last</strong> elements are each equal to the <strong>sum of all elements strictly between them</strong>.</li>
    </ul>
    <p>Your task is to return the total number of stable subarrays in the given array.</p>
    <h3>Example 1:</h3>
    <div class="sampleBox">capacity = [9, 3, 3, 3, 9]<br><strong>Output:</strong> 2</div>
</div>''',
        "starter_code": {
            "python": "class Solution:\n    def countStableSubarrays(self, capacity: list[int]) -> int:\n        # Write your solution here\n        return 0",
            "cpp": "#include <bits/stdc++.h>\nusing namespace std;\n\nclass Solution {\npublic:\n    long long countStableSubarrays(vector<long long>& capacity) {\n        // Write your solution here\n        return 0;\n    }\n};",
            "java": "class Solution {\n    public long countStableSubarrays(int[] capacity) {\n        // Write your solution here\n        return 0;\n    }\n}"
        },
        "sample_test_cases": [
            {
                "name": "Example 1",
                "input": '{"capacity": [9, 3, 3, 3, 9]}',
                "input_display": "capacity = [9, 3, 3, 3, 9]",
                "expected_output": "2"
            }
        ],
        "hidden_test_cases": [
            {
                "name": "No stable subarray",
                "input": '{"capacity": [1, 2, 3]}',
                "input_display": "capacity = [1, 2, 3]",
                "expected_output": "0"
            }
        ]
    }
}

COMPANY_TRACKS = {
    "google": {
        "name": "Google Software Engineer (L4/L5)",
        "description": "Focuses on optimal algorithmic design, graph & interval logic, and scale.",
        "q1_pool": ["two_sum", "stable_subarrays"],
        "q2_pool": ["merge_intervals", "longest_substring"]
    },
    "meta": {
        "name": "Meta Fast-Paced Algorithmic Track",
        "description": "Emphasis on two-pointers, sliding window, and clean production-ready code.",
        "q1_pool": ["two_sum"],
        "q2_pool": ["longest_substring", "merge_intervals"]
    },
    "amazon": {
        "name": "Amazon SDE + Leadership Principles",
        "description": "Algorithmic mastery paired with deep-dive scalability and operational trade-offs.",
        "q1_pool": ["two_sum", "stable_subarrays"],
        "q2_pool": ["merge_intervals", "stable_subarrays"]
    },
    "general": {
        "name": "General Fullstack & SDE Track",
        "description": "Standard comprehensive technical interview covering core Data Structures & Algorithms.",
        "q1_pool": ["two_sum", "stable_subarrays"],
        "q2_pool": ["merge_intervals", "longest_substring"]
    }
}

def get_track_problems(track: str = "general"):
    """Returns a randomized Q1 and Q2 tailored to the selected company track."""
    track_cfg = COMPANY_TRACKS.get(track.lower(), COMPANY_TRACKS["general"])
    
    q1_id = random.choice(track_cfg["q1_pool"])
    q2_id = random.choice(track_cfg["q2_pool"])
    
    # Ensure Q1 and Q2 are distinct
    if q1_id == q2_id:
        available_q2 = [pid for pid in track_cfg["q2_pool"] if pid != q1_id]
        if available_q2:
            q2_id = random.choice(available_q2)
        else:
            q2_id = "merge_intervals" if q1_id != "merge_intervals" else "longest_substring"
            
    return PROBLEMS[q1_id], PROBLEMS[q2_id], track_cfg
