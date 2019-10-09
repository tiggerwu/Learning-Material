#include <iostream>

using namespace std;

int quickSort(int *begin,int start,int end)
{
    int value = begin[start];
    int i = start;
    int j = end;

    while(i<j)
    {
        while(i<j&&value>begin[j])
        {
            j--;
        }
        if(i<j)
        {
            begin[i++]=begin[j];
        }
        while(i<j&&value<=begin[i])
        {
            i++;
        }
        if(i<j)
        {
            begin[j--]=begin[i];
        }
    }
    begin[j]=value;
    return j;
}

int find(int *begin,int start,int end,int k)
{
    int i=quickSort(begin,start,end);
    if (i==k-1) return begin[i];
    else if(i>k-1)
    {
        find(begin,start,i-1,k);
    }
    else
    {
        find(begin,i+1,end,k);
    }
}

int main()
{
    int n,k;

    cin >> n  >> k;

    int *number=new int[n];

    for(int i=0;i<n;i++)
    {
        cin>>number[i];
    }

    cout<<find(number,0,n-1,k);

    delete [] number;

    /*for(int i=0;i<n;i++)
    {
            cout << res[i];
    }*/



    return 0;
}
