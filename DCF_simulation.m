
function[simp,outp,acdelay,acdelay_sec]=DCF_simulation(n,W,q,runt,theta,K,t0,f0)
% simp: prob. of success
% outp: throughput
% acdelay: mean access delay
% acdelay_sec: second moment of access delay
% n: number of nodes
% W: initial backoff window size
% q: backoff factor, 0.5 for BEB
% runt: simulation time (in the unit of time slots)
% theta: aggregate traffci arrival rate
% K: maximum backoff stage
% t0: holding time of HOL packets in successful transmission
% f0: holding time of HOL packets in collision


lambdar=theta/n; 
aa=t0; %success slot basic
x0=f0; % -- collision basic
rts=f0;
%q=0.1;

%if flag==0
%    aa=180;
%    x0=175; % -- basic
%    rts=175;
%    q=(1-(1+1/192)*0.9)/(1-(1-x0/aa)*0.9-0.1*8/n*exp(-0.1/(1-(1-x0/aa)*0.9)))
%else
%    aa=192;
%    rts=9;
%    x0=9; %--rts
%    q=(1-(1+1/192)*0.97)/(1-(1-x0/aa)*0.97-0.03*8/n*exp(-0.03/(1-(1-x0/aa)*0.97)))
    %rts=14;
    %x0=14;
%end


a0=1/aa;
maxT=-lambertw(-exp(-1)/(1+1/x0))/(x0*a0-(1-x0*a0)*lambertw(-exp(-1)/(1+1/x0)));
pL=exp(x0*a0*theta/(1-(1-x0*a0)*theta)+lambertw(-(x0+1)*a0*theta/(1-(1-x0*a0)*theta)*exp(-x0*a0*theta/(1-(1-x0*a0)*theta))));
pS=exp(x0*a0*theta/(1-(1-x0*a0)*theta)+lambertw(-1,-(x0+1)*a0*theta/(1-(1-x0*a0)*theta)*exp(-x0*a0*theta/(1-(1-x0*a0)*theta))));

%q=-log(pS)/n;
%beta=q;
%K=1;
%q=(1-(1+1/aa)*maxT)/(1-(1-x0/aa)*maxT-(1-maxT)/(n*2/W)*exp(-(1-maxT)/(1-(1-x0/aa)*maxT)))
%q=0.5;

%K=4;
%K=6;

%qd=zeros(runt,1);

ql=zeros(n,1);
hols=zeros(n,1);
cons=zeros(n,1);

ns=zeros(n,1);
nre=zeros(n,1);
nne=zeros(n,1);


ToH=zeros(n,1);
frH=zeros(n,1);
acdelay=0;

%for second moment of access delay
acdelay_sec=0;

outp=0;
G=0;
mql=zeros(n,1);
p=zeros(n,1);
rou=zeros(n,1);

wins=zeros(n,1);
firh=zeros(n,1);

flagc=zeros(n,1);
flag_ch=0;
outqn=0;
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
                ns(outqn)=ns(outqn)+1; %success
                ql(outqn)=ql(outqn)-aa;
            else
                for I=1:n
                    if flagc(I)==1
                        hols(I)=hols(I)+1;
                        mwins=ceil(W*(1/q)^(min(hols(I),K)))-1;
                        %mwins=ceil(W/q*(min(hols(I),K))^2)-1;
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
                %sx=aa;
            else
                sx=rts;
                %sx=aa;
            end
            
        end
   end
           
    if mod(rt,1000000)==0
        rt/1000000
        %ql
        %for I=1:n
        %    p_int(I)=ns(I)/nre(I);
        %    mql_int(I)=mql(I)/rt/aa;
        %    rou_int(I)=nne(I)/rt;
        %end
        %mean(p_int)
        %mean(mql_int)*n/theta*aa
        %mean(rou_int)/lambdar*aa
        %outp*aa/rt;
        %inp*aa/rt;
    end
    time(u)=rt;
    pt(u)=sum(ns)/sum(nre);
       u=u+1;
end

%acdelay=acdelay/(outp*aa)
acdelay=acdelay/outp;
acdelay_sec=acdelay_sec/outp;
inp;
outp;
inp=inp*aa/rt;
outp=outp*aa/rt
ana=1-(1+W)/2/t0;
for I=1:n
    p(I)=ns(I)/nre(I);
    rou(I)=nne(I)/rt;
    mql(I)=mql(I)/rt/aa;
    %ps(I)=nci(I)/(nci(I)+nre0(I));
end


simp=mean(p)
simp2=sum(ns)/sum(nre);

%pl=exp(x0*a0*theta/(1-(1-x0*a0)*theta)+lambertw(-(x0+1)*a0*theta/(1-(1-x0*a0)*theta)*exp(-x0*a0*theta/(1-(1-x0*a0)*theta))))
%plot(time,pt,'--');
%simalfa=idt/rt

%alfa=1/((rts+1)-rts*pl-aa*pl*log(pl))
mean_rou=mean(rou);
%theta/n*(1+x0*a0*(1-pl)/pl+(1/pl+W*q/(q-1+pl))/2/alfa*a0)
%acdelay
simacd=mean(rou)/lambdar*aa;
simqd=mean(mql)*n/theta*aa;