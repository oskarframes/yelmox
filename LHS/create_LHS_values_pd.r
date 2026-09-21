# LHS ensemble
nr_v = 2
nr_s = 30

filename = paste("/home/hpc/gwgi/gwgi028h/yelmo/patagonia_dev/yelmox/LHS/lhs_np", nr_v, "_ns", nr_s, ".txt",sep="")
txt=read.table(filename,header=F, sep="")
a=as.matrix(txt)
colnames(a)=c("smbpal.sigma_melt","smbpal.sigma_snow")    # order of columns depending on Yelmo output
nr=nrow(a)
nc=ncol(a)

# convert 0 to 1 numbers to variable domains
# itmc, cgrz, kppgrz, fp, bt0, cffrzn, cfstrm, enhshr

# sima_melt: 5 - 10 ######itmc -10,-50
a[,1]=a[,1]*(10.0-5.0)+5.0

# sigma_snow: 5-10  ######itmb 1,4
a[,2]=a[,2]*(10.0-5.0)+5.0

# sland 5,10 
#a[,3]=a[,2]

# mmice (8,12)
#a[,4]=a[,4]*(12.000-(8.000))+(8.000)

# mmsnow (3,7)
#a[,5]=a[,5]*(7.000-(3.000))+(3.000)

# q (0,1)
#a[,6]=a[,6]*(1.000-0.000)+0.000

#cf (0.4,1.2)
#a[,7]=a[,7]*(1.200-0.400)+0.400

# u0 (10,100)
#a[,8]=a[,8]*(100.000-10.000)+10.000

# enh (1,4)
#a[,9]=a[,9]*(4.000-1.000)+1.020

# fp (0.02, 0.1)
#a[,10]=a[,10]*(0.100-0.020)+0.020

b=a
b[,1]=sprintf('%.3f', a[,1])
b[,2]=sprintf('%.3f', a[,2])
#b[,3]=sprintf('%.3f', a[,3])
#b[,4]=sprintf('%.3f', a[,4])
#b[,5]=sprintf('%.3f', a[,5])
#b[,6]=sprintf('%.3f', a[,6])
#b[,7]=sprintf('%.3f', a[,7])
#b[,8]=sprintf('%.3f', a[,8])
#b[,9]=sprintf('%.3f', a[,9])
#b[,10]=sprintf('%.3f', a[,10])

pairs(a, upper.panel=NULL)

# write the values in a txt file. 
out=format(b,digits=3,width=nr_v,justify="right", scientific=F)
filename = paste("/home/hpc/gwgi/gwgi028h/yelmo/patagonia_dev/yelmox/LHS/lhs_np", nr_v, "_ns", nr_s, "_values.txt", sep="")
write.table(out,file=filename,row.names=FALSE,col.names=TRUE,quote=FALSE)

