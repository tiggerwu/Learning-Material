#include <iostream>
#include <queue>

using namespace std;

struct task
{
    int order;
    int arrive;
    int time;

};

bool operator<(const task &x,const task &y)
{
    return x.order>y.order;
}

task Gettask()
{
    task tmp;

    cin>>tmp.order>>tmp.arrive>>tmp.time;

    return tmp;
}

int main()
{
  priority_queue<task> q;

  int number,time=0,index=0,result[100]={0};
  cin>>number;
  task tasks[number],tmp1,tmp2;

  for(int i=0;i<number;i++)
  {
      tasks[i]=Gettask();
  }

  for(int i=0;i<number;i++)
  {
      while(!q.empty())
      {
          tmp1=q.top();
          q.pop();
          tmp2=q.top();
          if((time+tmp1.time)<=tasks[i].arrive)
          {
              int flag = ((time + tmp1.time) == tasks[i].arrive);
              time=time+tmp1.time;
              result[index]=tmp1.order;
              index++;
              if(flag)
              {
                  break;
              }
          }
          else
          {
              tmp1.time=tmp1.time-tasks[i].arrive+time;
              q.push(tmp1);
              result[index]=tmp1.order;
              index++;
              time=time+tasks[i].arrive-time;
              break;
          }
      }
      tmp1.order=tasks[i].order;
      tmp1.time=tasks[i].time;
      q.push(tmp1);
      time=tasks[i].arrive;
  }

  while(!q.empty())
  {
      tmp1=q.top();
      q.pop();
      result[index]=tmp1.order;
      index++;
  }

  cout<<result[0]<<" ";
  for(int j=1;j<index;j++)
  {
      if(result[j]!=result[j-1])
      {
          cout<<result[j]<<" ";
      }
  }

  return 0;
}
