##SCRIPT PERMET DE TRANSFORMER FICHIER DIGIT EN CSV LISIBLE PAR HYDROSHOOT####


#####Fonction pour remettre le pot dans l'axe NORD/SUD que hydroshoot connait#####


Rotation <- function(xy,angleInDeg){
  #xy has to be a two column matrix
  newxy=xy
  
  for (row in (1:length(xy[,1]))){
   # print(row)
    newxy[row,1]=xy[row,1]*cos(angleInDeg*pi/180)+xy[row,2]*sin(angleInDeg*pi/180)
    newxy[row,2]=-xy[row,1]*sin(angleInDeg*pi/180)+xy[row,2]*cos(angleInDeg*pi/180)
  }
  
  return(newxy)
}

FindRotationForXnorth <- function(x1,y1,x2,y2){
  
  return(atan( (y2-y1)/(x2-x1)  ) / (pi/180) )
  
}

Convertor <- function(filename, path='',savepath=''){
  
  # we suppose that the variable 'filenames' includes a list of unique file names.
  
  #set.seed(which(filename == filenames))
  set.seed(1)
  
  data_i = read.csv(paste(path,filename,sep=""), header = T, sep=";")


  lines = which(data_i$annotation != "")

  fichier_resultats = as.data.frame(matrix(nrow = 0, ncol=10))
  colnames(fichier_resultats) = c("Plant",	"TRONC",	"ELMNT",	"SAR",	"RAM",	"RANG",	"Xabs",	"Yabs",	"Zabs"	,"DIAM")


  Nline=which(data_i[, "complementaire"] == "N")
  Sline=which(data_i[, "complementaire"] == "S")
  
  if (is.na(Nline)||is.na(Sline)){
    print("!!Error finding points of reference")
  }
  
  Properotation = FindRotationForXnorth(
    data_i[Nline, "X"],data_i[Nline, "Y"],data_i[Sline, "X"],data_i[Sline, "Y"]
  )
  
  oldNS=matrix(nrow=2,ncol=2)
  oldNS[1,]=c(data_i[Nline, "X"],data_i[Nline, "Y"])
  oldNS[2,]=c(data_i[Sline, "X"],data_i[Sline, "Y"])

  newNS=Rotation(oldNS,Properotation)
  
  if (newNS[1,1]<newNS[1,2]){
    Properotation=Properotation+180
  }
  
  acc = 1
  fichier_resultats[acc,10]=2*rnorm(1,1,0.1)

  for (line in lines)
  { 
  
    if (acc>1&&fichier_resultats[acc-1,10]!=0){
    
      fichier_resultats[acc,10]=fichier_resultats[acc-1,10]*runif(1,0.96,1)
    
    }
    else if (acc>1){
    fichier_resultats[acc,10]=fichier_resultats[acc-7,10]*runif(1,0.96,1)
    }
  
  
    if (data_i[line, "annotation"] == "o") 
    {
    
    
    
      ifelse(as.numeric(data_i[line, "complementaire"] == 0), 
           {rang = 0
            rameau = 0
            
    
      }, {#rang=as.numeric(data_i[line, "complementaire"])-1
        rameau = 1
        
        })
    
      fichier_resultats[acc,c("RAM","RANG")] = c(rameau, rang)
      fichier_resultats[acc,7:9] = data_i[line, 2:4]
      
      
      if (rameau!=0)
        rang = rang+1
      
      if (rang == 0 && data_i[line+1,"annotation"] == "f"){
        print(paste("ici",acc))
        print(fichier_resultats[acc:(acc+1),])
        fichier_resultats[acc+1,]=fichier_resultats[acc,]
        rameau = 1
        fichier_resultats[acc+1,5]=rameau
        fichier_resultats[acc,9]=fichier_resultats[acc,9]+0.5
        
        print(fichier_resultats[acc:(acc+1),])
        acc=acc+1
      }
      
      
      acc = acc + 1
    }
    if (data_i[line,"annotation"] == "f")
    {
    
    
    fichier_resultats[c(acc:(acc+6)),c("RAM")] = c("1","p","F1","F2","F3","F4","F5")
   
    fichier_resultats[c(acc:(acc+6)),c("RANG")] = c(rang, rep(0,6))
    for (i in 0:6){
      fichier_resultats[acc+i,7:9] = data_i[line+i, 2:4]
    }
    
    fichier_resultats[acc+1,10]=0.2*rnorm(1,1,0.1)
    fichier_resultats[(acc+2):(acc+6),10]=numeric(5)
    
    rang = rang+1
    acc = acc + 7
    }
  
  
  
  }

  fichier_resultats=rbind(numeric(10),fichier_resultats)
  fichier_resultats[1,9]=data_i[5,4]+runif(1,2,4)
  fichier_resultats[1,7]=runif(1,-0.5,0.5)+data_i[5,2]
  fichier_resultats[1,8]=runif(1,-0.5,0.5)+data_i[5,3]
  fichier_resultats[1,10]=runif(1,4.9,5.1)

  fichier_resultats[,1]=rep(1,length(fichier_resultats[,1]))
  fichier_resultats[,2]=rep(0,length(fichier_resultats[,1]))
  fichier_resultats[,3]=rep(1,length(fichier_resultats[,1]-1))
  fichier_resultats[,4]=rep(1,length(fichier_resultats[,1]-1))

  fichier_resultats[1,2:4]=c("base",0,0)

  fichier_resultats[,9]=-fichier_resultats[,9]

  fichier_resultats[,7]=fichier_resultats[,7]-fichier_resultats[1,7]
  fichier_resultats[,8]=fichier_resultats[,8]-fichier_resultats[1,8]
  
  fichier_resultats[,7:8]=Rotation(fichier_resultats[,7:8], Properotation-40)
  
  write.table(fichier_resultats,paste(savepath,"HS",filename,sep=""), row.names = FALSE, sep=';', dec='.')

}

###SORTIE DES FICHIERS

pathh = "E:/dossier_U/3.digitalisation/panel_30/geno_GIESCO/"
filenames = list.files(path = pathh)
savepath = "C:/Users/millanma/Documents/develop/hydroshoot_panel_digit_csv_sortie/"

for (i in 1:length(filenames)){
  
  Convertor(filenames[i],pathh,savepath)
  print(i)
}

#######creation 2 plantes par fichier

## fusionner deux fois mêmes plantes

library(tidyverse)
library(lubridate)
library(polynom)
library(ggplot2)
library(lme4)
library(dplyr)
library(ggrepel)
library(reshape2)
library(PerformanceAnalytics)
library(data.table)

setwd("C:/Users/millanma/Documents/develop/hydroshoot_panel_digit_csv_sortie/digits_stathis")
affenthale_5853 = read.csv("C:/Users/millanma/Documents/develop/hydroshoot_panel_digit_csv_sortie/digits_stathis/HSaffenthale$5853.csv", header = T, sep=";")

New_fichier= affenthale_5853
New_fichier$Yabs = New_fichier$Yabs + 20
New_fichier[,c("Xabs","Yabs")] = Rotation(New_fichier[,c("Xabs","Yabs")],180)

New_fichier_fusion = rbind(affenthale_5853, New_fichier)
write.csv2(New_fichier_fusion, "rotation.csv")
#write.csv2(New_fichier_fusion, "New_fichier_fusion.csv")

#boucle for

chemin = "C:/Users/millanma/Documents/develop/hydroshoot_panel_digit_csv_sortie/digits_stathis/"
filenames = list.files(path = chemin)
sauvegarde_path = "C:/Users/millanma/Documents/develop/hydroshoot_panel_digit_csv_sortie/plante_double/"
dat_fusion = NULL
for (i in 1:length(filenames))
  
  #i=filenames[[1]]
  {
  print(i)
  dat= read.csv(filenames[[i]], header=T, sep=";", dec = ".")
  dat_orig= read.csv(filenames[[i]], header=T, sep=";", dec = ".")
  dat$Yabs = dat$Yabs + 20
  dat[,c("Xabs","Yabs")] = Rotation(dat[,c("Xabs","Yabs")],180)
  dat$Plant = dat$Plant+1
  dat_fusion = rbind(dat_orig, dat)
  t= dat_fusion[dat_fusion$TRONC != "base", ]
  t[1, 2] = "base"; t
  
  #write.csv(dat_fusion, paste0(sauvegarde_path, i, ".csv"))
  #write_delim <- function(t, file, delim = ",")
  write.table(t, paste0(sauvegarde_path, filenames[[i]], ".csv"),row.names = FALSE, sep =";", dec = ".")
  
    print(filenames[[i]])
}



