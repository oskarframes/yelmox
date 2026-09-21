library(lhs)

#**************************************************************************************
# 3D LHS 
nr_s=100
nr_v=5
a=randomLHS(nr_s,nr_v)

a=round(a, digits=3)
#for(i in ncol(a)){
#  a[,i]=sprintf('%.3f', a[,i])
#}

out=format(a,digits=3,width=nr_v,justify="right", scientific=F)
filename = paste0("/home/hpc/gwgi/gwgi028h/yelmo/patagonia_dev/yelmox/LHS/lhs_251002_np", nr_v, "_ns", nr_s, ".txt")
write.table(out,file=filename,row.names=FALSE,col.names=FALSE,quote=FALSE)
cat("LHS table written: ",filename,"\n")

#pairs(a,upper.panel=NULL, pch=20)

