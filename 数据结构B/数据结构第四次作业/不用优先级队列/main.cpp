#include <iostream>

using namespace std;

struct task
{
    int order;
    int arrive;
    int time;

};

task Gettask()
{
    task tmp;

    cin>>tmp.order>>tmp.arrive>>tmp.time;

    return tmp;
}

int main()
{
    int number=0,sum=0;
    cin>>number;
    task tasks[number];

    for(int i=0;i<number;i++)
    {
        tasks[i]=Gettask();
    }

    for(int i=0;i<number;i++)
    {
        sum+=tasks[i].time;
    }

    int result[sum];

    for(int j=0;j<sum;j++)
    {
        int tmp_min=20,index=1;
        for(int i=0;i<number;i++)
        {
            if(tasks[i].arrive<=j&&tasks[i].order<tmp_min&&tasks[i].time!=0)
            {
                tmp_min=tasks[i].order;
                index=i;
            }
        }
        tasks[index].time-=1;
        result[j]=tasks[index].order;
    }

    cout<<result[0]<<" ";
    for(int j=1;j<sum;j++)
    {
        if(result[j]!=result[j-1])
        {
            cout<<result[j]<<" ";
        }
    }

    return 0;
}
