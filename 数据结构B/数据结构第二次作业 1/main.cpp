#include <cmath>
#include <stdlib.h>
#include <iostream>
#include <string>
#include <cstring>
using namespace std;

template<class elemType>

class seqStack
{
    private:
        elemType *elem;
        int top;
        int maxsize;

    public:
        seqStack(int initsize = 100)
        {
            elem = new elemType[initsize];
            maxsize = initsize;
            top = -1;
        }
        ~seqStack()
        {
            delete []elem;
        }
        void pop()
        {

            cout<<elem[top--];
        }
        void push(const elemType &x)
        {
            elem[++top]=x;
        }
};

int main()
{

    string s1,s2;
    getline(cin,s1);
    //bool flag=0;

    if(s1=="int")
    {
        //flag=1;
        //cout<<flag<<endl;
        seqStack<int> stack(100);
        int tmp;
        cin>>tmp;
        stack.push(tmp);
        cin>>tmp;
        stack.push(tmp);
        stack.pop();
        cout<<" ";
        cin>>tmp;
        stack.push(tmp);
        stack.pop();
        cout<<" ";
        stack.pop();
        cout<<" ";
        cin>>tmp;
        stack.push(tmp);
        cin>>tmp;
        stack.push(tmp);
        stack.pop();
        cout<<" ";
        stack.pop();
        cout<<" ";
    }
    else
    {
        seqStack<char> stack(100);
        char tmp;
        cin>>tmp;
        stack.push(tmp);
        cin>>tmp;
        stack.push(tmp);
        stack.pop();
        cout<<" ";
        cin>>tmp;
        stack.push(tmp);
        stack.pop();
        cout<<" ";
        stack.pop();
        cout<<" ";
        cin>>tmp;
        stack.push(tmp);
        cin>>tmp;
        stack.push(tmp);
        stack.pop();
        cout<<" ";
        stack.pop();
        cout<<" ";
    }

    return 0;
}
