      
function[simp,outp,acdelay,acdelay_sec, simalfa]=CSMA_Exp_CA_win(n,W,q,runt,theta,K,t0,f0)
lambdar=theta/n;
aa=t0; % success slot basic
x0=f0; % collision basic
rts=f0;

ql=zeros(n,1);
hols=zeros(n,1); % number of collisions
cons=zeros(n,1); % nodes Status. 0:wait,1:have transmission request

ns=zeros(n,1); % number of successful transmissions
nre=zeros(n,1); % number of transmission attempts 
nne=zeros(n,1);

ToH=zeros(n,1);
frH=zeros(n,1);
acdelay=0;

acdelay_sec=0; % for second moment of access delay

outp=0; % throughput
G=0;
mql=zeros(n,1);
p=zeros(n,1); % probability of successful transmission
rou=zeros(n,1);

wins=zeros(n,1); % backoff window
firh=zeros(n,1);

flagc=zeros(n,1); % nodes Status. 0:wait,1:have transmission request
flag_ch=0; % channel Status. 0:idle,1:busy
outqn=0; % index of node successfully transmitted
xn=0;
idt=0;
    u=1;
inp=0;
for rt=1:runt

    % generate new packets
    for I=1:n
        x=rand;
        if x<lambdar/aa
            inp=inp+1;
            ql(I)=ql(I)+aa;
        end
        mql(I)=mql(I)+ql(I);
    end
    

    % set the transmission requests
    cons=zeros(n,1);
    for I=1:n
        if ql(I)~=0
            %set the time tag for the fresh HOL packet of each queue
            if frH(I)==0
                ToH(I)=rt;
                frH(I)=1;
            end
            
           
            % check the queue status and sense the channel
            if flag_ch==0           % channel is idle
                if firh(I)==0
                    mwins=W-1;
                    wins(I)=floor(rand*mwins);
                    firh(I)=1;
                else
                    if wins(I)==0
                        cons(I)=1;
                        nre(I)=nre(I)+1; %transmission attempt
                    else
                        wins(I)=wins(I)-1;
                    end
                end
            end
            nne(I)=nne(I)+1;
        end
    end

    % calculate the attempt rate
    if flag_ch==0
        G=G+sum(cons);
        idt=idt+1;
    end

    % set the channel status
    if flag_ch==1  % channel is busy
        if xn==sx   % xn represents the no. of transmission slots now 
            flag_ch=0;            
            xn=0;
            if sum(flagc)==1
                [a b]=max(flagc);
                outqn=b;
                
                %calculate the output
                outp=outp+1;
           
                %calculate the access delay
                acdelay=acdelay+rt-ToH(outqn);
                
                acdelay_sec=acdelay_sec+(rt-ToH(outqn))^2;
                
                frH(outqn)=0;
                
                firh(outqn)=0;
                hols(outqn)=0;
                ns(outqn)=ns(outqn)+1; % success
                ql(outqn)=ql(outqn)-aa;
            else
                for I=1:n
                    if flagc(I)==1 
                        hols(I)=hols(I)+1;
                        mwins=ceil(W*(1/q)^(min(hols(I),K)))-1;
                        wins(I)=floor(rand*mwins);
                    end
                end
            end
        else
            xn=xn+1;
        end
    else
        if sum(cons)~=0
            flagc=cons;
            xn=1;
            flag_ch=1;
            if sum(cons)==1
                sx=aa;
            else
                sx=rts;
            end
            
        end
    end
   

    if mod(rt,1000000)==0
        rt/1000000;
    end
    time(u)=rt;
    pt(u)=sum(ns)/sum(nre);
       u=u+1;
end

acdelay=acdelay/outp;
acdelay_sec=acdelay_sec/outp;
inp=inp*aa/rt;
outp=outp*aa/rt;
for I=1:n
    p(I)=ns(I)/nre(I);
    rou(I)=nne(I)/rt;
    mql(I)=mql(I)/rt/aa;
end


simp=mean(p);
simp2=sum(ns)/sum(nre);

%pl=exp(x0*a0*theta/(1-(1-x0*a0)*theta)+lambertw(-(x0+1)*a0*theta/(1-(1-x0*a0)*theta)*exp(-x0*a0*theta/(1-(1-x0*a0)*theta))))
%plot(time,pt,'--');
simalfa=idt/rt;

    