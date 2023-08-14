#!/usr/bin/env bash
#set -o nounset -o pipefail 
#set -e # exit @error
#set -u # unset unbound variable treat as error var
#set -x # debug mode display executed commands
#shellcheck :TODO:

#----------------------------------------#
# Usage: . ./krop.sh AUTHOR/PAPER.pdf
#
# Run this script  in docker container.
# krop-master   http://arminstraub.com/software/krop
#   https://www.pdflabs.com/tools/pdftk-the-pdf-toolkit/
# apt install poppler-utils pdftk ghostscript
#
#----------------------------------------#

RED='\033[0;31m'
NC='\033[0m' # No Color
ITALIC='\033[3m'
LBLUE='\e[94m'
LYELLOW='\e[93m'
DIM='\e[2m'
BLINK='\e[5m'

if [ $# -ne 2 ]
    then 
        printf "${RED}Usage: . ./krop.sh AUTHOR/[PAPER.pdf]${NC} [YYYY_Mon]\n"
        printf "example: . ./krop.sh ALFORD/subquantal.pdf  2023_Jul\n"
        return
        #(exit 33) && true # return exit code w/o return shell, -e active but avoid return shell
fi

# paper dir
t=$(echo "${1}" | grep -F -e "/")
if [ $? -eq 1 ]; then
    printf "Usage: . ./krop.sh ${RED}AUTHORDIR/[PAPER.pdf]${NC} [YYYY_Mon]\n"
    printf "\t\t# author dir required\n"
    return
fi

AUTHORDIR=${1%/*}
PAPER=${1##*/} 
CROPPED=${PAPER%*.pdf}-cropped.pdf
PDFS=${PAPER%*.pdf}_pdfs
PNGS=${PAPER%*.pdf}_pngs
CSV=${AUTHORDIR}_${PAPER%*pdf}csv

# 1. GUI krop
 #_container_:$krop  //run gui
echo "----------------------------------------"
# krop exist
if ! command -v krop $1 &> /dev/null
then
    echo "krop could not be found"
    return
else
    printf "${LYELLOW}While running krop in ${AUTHORDIR}/:\n"
    printf "open ${PAPER}${NC}${DIM} and${NC}${LYELLOW} save cropped as ${CROPPED}\n"
    krop $1 &
fi

printf "\n${RED}Press any key to continue...${NC}\n"
echo "----------------------------------------"
read -n 1
clear 


#----------------------------------------#
# 2. create dirs and csv file
cd ${AUTHORDIR} && mkdir -p ${PDFS} ${PNGS}

numpgs="$(pdfinfo ${CROPPED} | grep Pages | awk -F: '{print $2}')"

printf "${LYELLOW}pdf -> pages -> pngs -> csv ${NC}\n"
echo $CSV 
tag="${CSV%*.csv}_paper"
echo "tags:${tag} ${2}" | tee $CSV


function pngs()
{
    fbase=${1#*/}
    file="${tag}_${fbase%*pdf}png"
    #echo "${file}"
    gs -o "${PNGS}/${file}" \
        -sDEVICE=pngalpha \
        -dLastPage=1 \
        -r144 "$1" -q >> gs.log 2>&1
    # flatten transparent background
}

# 1. pdf to pages 
pdftk ${CROPPED} burst output ${PDFS}/page_%04d.pdf   

# 2. pages to pngs function
for f in "${PDFS}"/*"pdf"; do pngs "${f}"; done          


# 3. create csv file
for ff in "${PNGS}"/*"png"; 
do 
    echo "<img src=\"${ff#*/}\">" | tee -a $CSV
done 
printf "${LYELLOW} confirm ${numpgs} ${NC}\n"
printf "\n${RED}Press any key to continue...${NC}\n"
echo "----------------------------------------"
read -n 1
#clear -x
clear


#----------------------------------------
MEDIA="/home/valence/.local/share/Anki2/User 1/collection.media"

echo "----------------------------------------\n"
printf "${LYELLOW}Copy media${NC}\n"
printf "${LYELLOW}Check files before manual copy-paste cmd:\n %s ${NC}\n" $CSV

echo 'for f in '"${PNGS}"'/*png;do fm="${f#*/}";echo ccp "${f}" "'"${MEDIA}"'/${fm}";done' > copy.cmd

cat copy.cmd
printf "\n${RED}Press any key to continue...${NC}\n\
----------------------------------------\n"
read -n 1

# import csv
printf "\n${LYELLOW}Anki import csv\n\t:: do not html format, field separate by Colon${NC}\n\n"
echo "notetype:scanned_notebook"
echo "deck:Default"
echo "Fields separate by tab \\t"
cd ..
## errata
##numpgs=$(pdfinfo ${CROPPED} | grep Pages | awk -F: '{print $2}'
## xdg-open png/
## sushi preview with spacebar
