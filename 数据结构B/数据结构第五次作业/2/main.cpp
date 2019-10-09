#include <iostream>

using namespace std;

int count[50]={0};

class closeHashTable
{
    private:
        struct node
        {
            int data;
            int state;

            node(){state=0;}
        };

    public:
        node *array;
        int size;
        closeHashTable(int length=101)
        {
            size=length;
            array=new node[size];
            for(int i=0;i<size;i++)
            {
                array[i].data=-1;
            }
        }
        void insert(const int &x,const int &p)
        {
            int count_tmp=0;
            int initPos,pos;

            initPos=pos=x%p;
            do
            {
                if(array[pos].state!=1)
                {
                    array[pos].data=x;
                    array[pos].state=1;
                    count_tmp++;
                    count[pos]=count_tmp;
                    return;
                }
                count_tmp++;
                pos=(pos+1)%size;
            }while(pos!=initPos);
        }
};


int main()
{

    int p,m,n;
    cin>>p>>m>>n;
    closeHashTable table(m);
    int tmp;
    for(int i=0;i<n;i++)
    {
        cin>>tmp;
        table.insert(tmp,p);
    }
    for(int i=0;i<m;i++)
    {
        cout<<i<<" ";
    }
    cout<<endl;
    for(int i=0;i<m;i++)
    {
        cout<<table.array[i].data<<" ";
    }
    cout<<endl;
    for(int i=0;i<m;i++)
    {
        cout<<count[i]<<" ";
    }
    return 0;
}
