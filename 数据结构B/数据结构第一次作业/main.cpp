#include <cmath>
#include <stdlib.h>
#include <iostream>
#include <string>
#include <cstring>
using namespace std;


class node
{
	public:
        float coe;
        int exp;
        node *next;

        node(float c, int e, node *p = NULL):coe(c),exp(e),next(p){}
        node(){next = NULL;}
        ~node(){delete next;}
};

node* Create(string p)
{
	string tmp;
	char temp[1000];
	node* head;
	node*s;
	float c=0;
	int e=0;
	s = head = new node;
	head->next = NULL;

    int start=0;
    int end=0;

    int last = p.rfind(',');
	int len = int(p.length());
	for (int i = 0;i < len;i++)
	{
		if (p[i] == ',')
		{
            end = i  ;
            tmp = p.substr(start,end);
            strcpy(temp,tmp.c_str());
            start = i + 1;

			c= atof(temp);

		}
		if (p[i] == ' ')
		{
			end = i;
			tmp = p.substr(start,end);
            strcpy(temp,tmp.c_str());
            start = i + 1;
            e= atoi(temp);

            s->next = new node(c,e);
            s=s->next;
		}
		if(i==last)
		{
		    end = len;
            tmp = p.substr(start,end);
            strcpy(temp,tmp.c_str());
            e = atoi(temp);

            s->next = new node(c,e);
            s=s->next;
            s->next=NULL;
		}
	}
	return head;
}

node* Multiply(node* a,node* b)
{
    node* na,*nb;
    na = a->next;
    nb = b->next;
    float coe;
    int exp;

    node* res,*p;

    res=p=new node;
    while(na!= NULL)
    {

        while(nb != NULL)
        {

            coe=na->coe*nb->coe;
            exp=na->exp+nb->exp;

            p->next=new node(coe,exp);
            p=p->next;
            nb = nb->next;

        }
        nb = b->next;
        na=na->next;
    }
    p->next=NULL;

    return res;


}

void Combine(node *head)
{
    node *p1,*p2;
    float tmp;

    p1=head->next;
    while(p1!=NULL)
    {
        p2 = p1->next;
        while(p2!=NULL)
        {
            if(p1->exp==p2->exp)
            {

                tmp=p1->coe+p2->coe;
                p1->coe=tmp;
                p1->next=p2->next;
            }
            p2=p2->next;
        }
        p1=p1->next;
    }
}


void Sort(node *s)
{
    node *p,*q,*o,*tmp,*head;
    head=s;
    p=head;
    o=head->next->next;
    head->next->next=NULL;

    while(o)
    {
        //for(tmp=o,q=head->next;(q!=NULL)&&(q->exp<tmp->exp);p=q,q=q->next);
        tmp=o;
        for(q=head->next;q!=NULL;)
        {
            p=q;
            q=q->next;
            if(q->exp>=tmp->exp)break;
        }

        o=o->next;
        if(q==head->next)head->next=tmp;
        else p->next=tmp;
        tmp->next=q;
    }
}

void Display(node *head)
{
	node* p;
	p=head->next;
	while (p->next!= NULL)
	{
		cout << p->coe << ',' << p->exp << ' ';
		p=p->next;
	}
	cout << p->coe << ',' << p->exp;

}
int main()
{
	string p1, p2;
	node *e1, *e2;
	node *s1;

	getline(cin, p1);
	e1 = Create(p1);
	getline(cin, p2);
	e2 = Create(p2);

	s1=Multiply(e1,e2);

    Sort(s1);

	Combine(s1);

	Display(s1);

	return 0;

}
