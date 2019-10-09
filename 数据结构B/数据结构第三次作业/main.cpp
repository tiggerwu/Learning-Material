#include <iostream>
#include <string>
#include <cstring>
#include <cmath>
#include <stdio.h>
#include <stdlib.h>
#include <vector>

using namespace std;

/*class bTree
{
    private:
        struct node
        {
            node *left,*right;
            char data;

            node():left(NULL),right(NULL){}
            node(char item,node *L=NULL,node *R=NULL):data(item),left(L),right(R){}
            ~node(){}
        };
        node *root;

    public:
        bTree():root(NULL){}
        bTree(char x){root = new node(x);}
        ~bTree();

};*/

typedef struct btnode
{
    struct btnode *left,*right;
    char data;

}btnode,*bTree;

void Create(bTree &T)
{
    char ch;
    scanf("%c",&ch);
    if(ch=='#')T=NULL;
    else
    {
        T=(bTree)malloc(sizeof(btnode));
        if(!T)exit(-1);
        T->data=ch;
        Create(T->left);
        Create(T->right);
    }
}

int i=0,j=0,count1=0;
int count[1000]={0};
char s[1000][100];

void FindAllPath(btnode *root, vector<char> path)
{
	if (root != NULL)
	{
		path.push_back(root->data);
		if (root->left == NULL && root->right == NULL)
		{
			count1=0;
			j=0;
			for (vector<char>::iterator iter=path.begin(); iter!=path.end(); iter++)
			{
				s[i][j]=*iter;
				count1++;
				j++;
			}
			count[i]=count1;
			i++;
			return;
		}
		else
		{
			FindAllPath(root->left, path);
			FindAllPath(root->right, path);
		}
	}
}

int main()
{
    bTree T=NULL;
    Create(T);
    vector<char> path;
    FindAllPath(T,path);
    int max=0,index=0,k=0;
    for(k=0;k<=i;k++)
    {
        if(count[k]>max)
        {
            max=count[k];
            index=k;
        }
    }

    cout<<max<<endl;
    cout<<s[index];

    return 0;
}
