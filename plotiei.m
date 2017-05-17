clear all
close all

basename='ca3net8_gamma62_lif_pyr_rec_5hz_mua';

muadat=importdata([basename '.dat']);
time=muadat(:,1);
mua=muadat(:,2);
figure(1)
plot(time,mua)

eventdat=importdata([basename '_LP_SPKS.txt']);
events=eventdat.data;
hold
plot(events,10,'rx')

ieidat=importdata([basename '_LP_SPKS_IEI.txt']);
bins=ieidat.data(1,:);
counts=ieidat.data(2,:);
figure
bar(bins,counts)

ieis_raw=diff(events);
events_corr=events(ieis_raw>15);
figure(1)
plot(events_corr,10,'go')

ieis_corr=diff(events_corr);
counts_corr=hist(ieis_corr,2:4:198);
figure
bar(2:4:198,counts_corr)
