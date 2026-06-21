set datafile separator "\t"
set terminal pngcairo size 1800,1100 enhanced font "Arial,11"
set output outfile

set multiplot layout 3,1 title "Historico de Performance das Execucoes"

set grid
set key left top
set xlabel "Execucoes (mais velha -> mais nova)"
set xtics rotate by 35 right
set format y "%.2f"

set ylabel "Tempo (s)"
plot datafile every ::1 using 1:3:xticlabels(2) with linespoints lw 2 pt 7 title "Tempo total", \
     '' every ::1 using 1:3:(sprintf("%.2f", $3)) with labels offset 0,1 tc rgb "#7f00ff" notitle, \
     datafile every ::1 using 1:4:xticlabels(2) with linespoints lw 2 pt 5 title "Tempo de CPU", \
     '' every ::1 using 1:4:(sprintf("%.2f", $4)) with labels offset 0,-1 tc rgb "#009688" notitle

set ylabel "CPU medio (%)"
plot datafile every ::1 using 1:5:xticlabels(2) with linespoints lw 2 pt 9 title "CPU medio", \
     '' every ::1 using 1:5:(sprintf("%.2f", $5)) with labels offset 0,1 tc rgb "#7f00ff" notitle

set ylabel "Memoria (MB)"
plot datafile every ::1 using 1:6:xticlabels(2) with linespoints lw 2 pt 11 title "Pico de memoria", \
     '' every ::1 using 1:6:(sprintf("%.2f", $6)) with labels offset 0,1 tc rgb "#7f00ff" notitle

unset multiplot
