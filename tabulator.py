#!/usr/bin/env python

'''
Tabulator main
'''

from glob import glob
import argparse
import cv2

from convert import Converter
from plot_rectangles import PlotRectangles
from xAxis import XAxis
from yAxis import YAxis
from plotname import PlotName
from legends import Legends
from pdfGen import PdfGen
from data import Data

parser = argparse.ArgumentParser(
  description='Computes data from the plots in the given PDF')

parser.add_argument('--inp', type=str, help='Path of the input pdf')
parser.add_argument('--out', type=str, help='Path of the output pdf')
parser.add_argument('--csv', type=bool, default=False, help='True if data to be written in csv format also')
parser.add_argument('--no_interrupt', type=bool, default=False, help='True if user does not want to enter text recognition data if OCR fails.\
  In that case, values shall be given in terms of pixels')

def main():
  args = parser.parse_args()

  fns = glob(args.inp)

  if len(fns) == 0:
    print "\nNo input file found, please check input path\n"
    exit(1)

  pdf_gen = PdfGen(args.out, args.csv)

  for index, fn in enumerate(fns):
    pdf_gen.writePdfName(fn)

    img = Converter().convertPDF(fn)

    rectangles = PlotRectangles().getRectangles(img)

    x_axis = XAxis(img.copy())
    y_axis = YAxis(img.copy())
    plot_name = PlotName(img.copy())
    

    #iterating over tables
    for i, rectangle in enumerate(rectangles):
      plotFilename = '/tmp/plot.png'
      x1,y1 = rectangle[0]
      x2,y2 = rectangle[2]
      cv2.imwrite(plotFilename, img[y1:y2, x1:x2].copy())

      try:
        ret = x_axis.findXScale(rectangle, i, args.no_interrupt)
      except:
        ret = [100, 10, 0, 100]

      xLabelPath, mx = x_axis.findXLabel(rectangle, ret[1], i, index)
      xScale = ret[0]
      xStart = ret[2]
      xDelta = ret[3]

      try:
        ret = y_axis.findYScale(rectangle, i, args.no_interrupt)
      except:
        ret = [100, 10, 0, 100]

      yLabelPath = y_axis.findYLabel(rectangle, ret[1], i, index)
      yScale = ret[0]
      yStart = ret[2]
      yDelta = ret[3]

      plotNamePath = plot_name.getPlotName(rectangle, i, index, mx)

      legends = Legends(rectangle, img)
      legendItemImagePaths, colorMap = legends.getLegend(i, index)
      
      data = Data().getData(plotFilename, xStart, xDelta, xScale, yStart, yDelta, yScale, colorMap)

      table_headers = [xLabelPath] + legendItemImagePaths
      pdf_gen.add_table(plotNamePath, yLabelPath, table_headers, data)

  pdf_gen.print_file()

if __name__ == '__main__':
  main()