---
  title: "hydroshoot"
output: html_document
date: "2023-04-25"
---
  #Chargement des fichiers csv
  
library(tidyverse)
library(lubridate)
library(lme4)
library(ggplot2)
library(dplyr)
library(agricolae)
library(broom)
library("ggpubr")
library(tidyr)
library(patchwork)
library(rlist)
library(RColorBrewer)
library(pdftables)


setwd("F:/DOCTORAT_MILLAN/experimentations/hydroshoot/clear_sky")
midi_clear = read.csv("summary_props_12h.csv", sep=';', dec=".")


##### CLEAR DAY
dat=midi_clear
info= read.csv("time_series_all_selection_combis.csv", sep=';', dec=".")
info= info[info$heure == "00:00:00",]
result = as.data.frame(matrix(nrow = 0, ncol = 2))
colnames(result)= c("combi", "Tlc")
param = 0.1 # permet de regler si je veux 10% des plus chaud (0.1) ou 20% (0.2) etc
i=0

for (geno in unique(as.factor(dat$combi))){
  i=i+1
  print(geno)
  dat_plante = dat[as.factor(dat$combi) == geno,]
  dat_plante = dat_plante[order(dat_plante$Tlc, decreasing = T),]
Max_Tlc = mean(dat_plante$Tlc[c(1:round(param*dim(dat_plante)[1],0))])
result[i,]= c(geno,Max_Tlc)
}

write.csv(result, "direct_light.csv", row.names = F)
result_plant = read.csv("time_series_all_selection_combis.csv", sep=';', dec=".")

hist(as.numeric(result$Tlc), xlim=c(30,33))
result[,c("R", "LEN", "SF")] = info[match(result$combi, info$combi),c("r","len","la")]


mod = lm(result$Tlc ~ result$LEN * result$R * result$SF)
print(mod)
mod = lm(result$Tlc ~ result$LEN + result$R + result$SF)
print(mod)

#mod = lm(AS_11_07_13h$t_q50 ~ AS_11_07_13h$LEN * AS_11_07_13h$R + AS_11_07_13h$LEN * AS_11_07_13h$SF + AS_11_07_13h$SF *AS_11_07_13h$R)


result =result[order(result$Tlc),]
plot(result$Tlc ~ result$LEN)
plot(result$Tlc ~ result$SF)
plot(result$Tlc ~ result$R)

plot(result_plant$E ~ result_plant$len)
plot(result_plant$E ~ result_plant$la)
plot(result_plant$E ~ result_plant$r)


plot(result$SF ~ result$LEN)
library(rgl)
plot3d (result$SF, result$LEN, result$R)


##### CLoudy DAY

setwd("F:/DOCTORAT_MILLAN/experimentations/hydroshoot/cloudy_sky")
midi_cloudy = read.csv("summary_props_12h.csv", sep=';', dec=".")

dat=midi_cloudy
info= read.csv("time_series_all.csv", sep=';', dec=".")
info= info[info$heure == "00:00:00",]
result = as.data.frame(matrix(nrow = 0, ncol = 2))
colnames(result)= c("combi", "Tlc")
param = 0.1 # permet de regler si je veux 10% des plus chaud (0.1) ou 20% (0.2) etc
i=0

for (geno in unique(as.factor(dat$combi))){
  i=i+1
  print(geno)
  dat_plante = dat[as.factor(dat$combi) == geno,]
  dat_plante = dat_plante[order(dat_plante$Tlc, decreasing = T),]
  Max_Tlc = mean(dat_plante$Tlc[c(1:round(param*dim(dat_plante)[1],0))])
  result[i,]= c(geno,Max_Tlc)
}

write.csv(result, "diffused_light.csv", row.names = F)
diffused_light = read.csv("diffused_light.csv", sep=';', dec=".")

result_plant = read.csv("time_series_all.csv", sep=';', dec=".")

hist(as.numeric(diffused_light$Tlc), xlim=c(24,26))
result[,c("R", "LEN", "SF")] = info[match(result$combi, info$combi),c("r","len","la")]
diffused_light[,c("R", "LEN", "SF")] = info[match(diffused_light$combi, info$combi),c("r","len","la")]

mod_1 = lm(result$Tlc ~ result$LEN * result$R + result$SF *result$LEN + result$SF *result$R)
print(mod_1)
mod_2 = lm(result$Tlc ~ result$LEN + result$R + result$SF)
print(mod_2)

result =result[order(result$Tlc),]
plot(result$Tlc ~ result$LEN)
plot(result$Tlc ~ result$SF)
plot(result$Tlc ~ result$R)


plot(result_plant$Rg ~ result_plant$len)
plot(result_plant$Rg ~ result_plant$la)
plot(result_plant$Rg ~ result_plant$r)

plot(result_plant$E ~ result_plant$len)
plot(result_plant$E ~ result_plant$la)
plot(result_plant$E ~ result_plant$r)

plot(result$SF ~ result$LEN)

result= diffused_light

library(rgl)
colors = rainbow()
legend3d("topright", legend = c(min("LEN"), max("LEN")), col = colors, lty = 1)

library(grDevices)
library(RColorBrewer)
my_palette <- topo.colors(50) # in package grDevices
n_colors <- length(my_palette)
my_palette = rev(brewer.pal(n = 11, name = "RdBu"))
n_colors <- length(my_palette) 
 
# plot(combi_18$x_bot_position, combi_18$z_bot_position,col=my_palette[ceiling((combi_18$Tlc-min(combi_18$Tlc))/
#                          (max(combi_18$Tlc)-min(combi_18$Tlc))*(n_colors-1))+1], pch = 16, xlim = c(-65,65), ylim =c(30,150)
#      , main = paste0("Tleaf", geno))
result$Tlc = as.numeric(result$Tlc)
result = result[!(result$Tlc == max(result$Tlc)),]
plot3d (result$SF, result$LEN, result$R, col=my_palette[ceiling((result$Tlc-min(result$Tlc, na.rm = T))/
                                             (max(result$Tlc, na.rm = T)-min(result$Tlc, na.rm = T))*(n_colors-1))+1])

par(mfrow = c(2,2))
mean_result_R = aggregate(data.frame(result$Tlc,result$R), by = list(result$SF, result$LEN), mean)
colnames(mean_result_R) = c("SF", "LEN", "Tlc", "R")
plot (mean_result_R$SF, mean_result_R$LEN, col=my_palette[ceiling((mean_result_R$Tlc-min(mean_result_R$Tlc, na.rm = T))/
                                                                  (max(mean_result_R$Tlc, na.rm = T)-min(mean_result_R$Tlc, na.rm = T))*(n_colors-1))+1])

mean_result_LEN = aggregate(data.frame(result$Tlc,result$LEN), by = list(result$SF, result$R), mean)
colnames(mean_result_LEN) = c("SF", "R", "Tlc", "LEN")

plot (mean_result_LEN$SF, mean_result_LEN$R, col=my_palette[ceiling((mean_result_LEN$Tlc-min(mean_result_LEN$Tlc, na.rm = T))/
                                                      (max(mean_result_LEN$Tlc, na.rm = T)-min(mean_result_LEN$Tlc, na.rm = T))*(n_colors-1))+1])

mean_result_LEN$color= ceiling((mean_result_LEN$Tlc-min(mean_result_LEN$Tlc, na.rm = T))/
                      (max(mean_result_LEN$Tlc, na.rm = T)-min(mean_result_LEN$Tlc, na.rm = T))*(n_colors-1))+1

mean_result_SF = aggregate(data.frame(result$Tlc,result$SF), by = list(result$LEN, result$R), mean)
colnames(mean_result_SF) = c("LEN", "R", "Tlc", "SF")

plot (mean_result_SF$R, mean_result_SF$LEN, col=my_palette[ceiling((mean_result_SF$Tlc-min(mean_result_SF$Tlc, na.rm = T))/
                                                      (max(mean_result_SF$Tlc, na.rm = T)-min(mean_result_SF$Tlc, na.rm = T))*(n_colors-1))+1])

ggplot(data=diffused_light, aes(x=combi, y=Tlc)) +
  geom_point()+
scale_y_continuous(limits=c(24,26))+
scale_x_continuous(limits=c(0,1000))+
  theme_bw()+
  theme(axis.text.y = element_text(face= "bold", size = 15, color="black"), axis.title.x = element_blank())+
  theme(axis.text.x = element_text(face= "bold", size = 15, color="black", angle=45, vjust = 0.5),
        axis.line = element_line(size = 1.3, colour = "black", linetype= "solid"))
