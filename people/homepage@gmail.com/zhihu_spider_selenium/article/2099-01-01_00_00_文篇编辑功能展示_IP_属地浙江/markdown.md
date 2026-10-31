# 一级标题
## 二级标题

>引用

**加粗字体**

网址：[http://121.40.168.141](http://121.40.168.141)

### code
```
class Solution {
public:
    string convert(string s, int numRows) {
        string ret, tmp[numRows];
        int i = 0;
        while(i < s.length()) {
            for(int k = 0; k < numRows && i < s.length(); k++) {
                tmp[k] += s[i++];
            }
            for(int k = numRows-2; k > 0 && i < s.length(); k--) {
                tmp[k] += s[i++];
            }
        }
        for(int k = 0; k < numRows; k++) {
            ret += tmp[k];
        }
        return ret;
    }
};
```

