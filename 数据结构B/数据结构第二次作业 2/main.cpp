#include <cmath>
#include <stdlib.h>
#include <iostream>
#include <string>
#include <cstring>
#include <stack>

using namespace std;

stack<char> tmp;

int pri(char ch)
{
    int res=0;

    switch(ch)
    {
        case '+':res = 1;break;
        case '-':res = 1;break;
        case '*':res = 2;break;
        case '/':res = 2;break;
    }

    return res;
}

int main()
{

    string s;
    char ch[100],temp;

    getline(cin,s);
    strcpy(ch,s.c_str());
    int len = s.length();

    for(int i=0;i<len;i++)
    {
        if(ch[i]>='a'&&ch[i]<='z')
            cout<<ch[i];
        else if(ch[i]=='('||ch[i]==')')
        {
            if(ch[i]=='(')
               tmp.push(ch[i]);
            else
            {
                while(tmp.top()!='(')
                      {
                          temp = tmp.top();
                          tmp.pop();
                          cout << temp;
                      }
                tmp.pop();
            }
        }
        else
        {
            while(true)
            {
                //cout<<tmp.empty();
                if(tmp.empty()||tmp.top()=='(')
                {
                    tmp.push(ch[i]);
                    break;
                }
                else if(pri(tmp.top())<pri(ch[i]))
                {
                    tmp.push(ch[i]);
                    break;
                }
                else
                {
                    temp = tmp.top();
                    tmp.pop();
                    cout<<temp;
                }

            }
        }
    }

    while(!tmp.empty())
    {
        temp = tmp.top();
        tmp.pop();
        cout<<temp;
    }
}
