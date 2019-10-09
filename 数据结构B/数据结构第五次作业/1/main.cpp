#include<iostream>

using namespace std;

int res[50]={0};
int j=0;
/*for(int i=0;i<50;i++)
{
    res[i]=-1;
}*/

    struct node {
        int data;
        node *left,*right;

        node(const int &num,node *l=NULL,node *r=NULL):data(num),left(l),right(r){}
        };


    int find(const int &x,node *&t)
    {

      if(t==NULL)
      {
          cout<<-1<<endl;
          return 0;
      }
      else if(t->data==x)
      {
          cout<<1<<endl;
          res[j]=t->data;
          j++;
          return 0;
      }
      if(x<t->data)
      {
          res[j]=t->data;
          j++;
          return find(x,t->left);
      }
      else
      {
          res[j]=t->data;
          j++;
          return find(x,t->right);
      }
    }

    void insert(const int&x,node*&t)
    {
        if(t==NULL)
            t=new node(x,NULL,NULL);
        else if(x<t->data)
            insert(x,t->left);
        else if(x>t->data)
            insert(x,t->right);
    }


int main()
{

    node *head=NULL;
    int n,tmp,x;
    cin>>n;
    for(int i=0;i<n;i++)
    {
        cin>>tmp;
        insert(tmp,head);
    }
    cin>>x;
    find(x,head);
    for(int i=0;res[i]!=0;i++)
    {
        cout<<res[i]<<" ";
    }

    return 0;
}
