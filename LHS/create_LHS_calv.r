library(lhs)

#**************************************************************************************
# 3D LHS 
ns = 10
np = 1
a=randomLHS(ns,np)

a=round(a, digits=3)
#for(i in ncol(a)){
#  a[,i]=sprintf('%.3f', a[,i])
#}

out=format(a,digits=3,width=3,justify="right", scientific=F)
filename = paste0("/home/hpc/gwgi/gwgi028h/yelmo/patagonia_dev/yelmox/LHS/lhs_np", np, "_ns", ns, "_calv.txt")
write.table(out,file=filename,row.names=FALSE,col.names=FALSE,quote=FALSE)
cat("LHS table written: ",filename,"\n")

#pairs(a,upper.panel=NULL, pch=20)

