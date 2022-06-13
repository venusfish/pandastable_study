# DataExplore Application based on pandastable
from __future__ import absolute_import
from test.app_study import DataExplore, TestApp

def main():
    """Run the application from outside the module - used for
       deploying as frozen app"""

    import sys, os
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-f", "--file", dest="msgpack",
                        help="Open a dataframe as msgpack", metavar="FILE")
    parser.add_option("-p", "--project", dest="projfile",
                        help="Open a dataexplore project file", metavar="FILE")
    parser.add_option("-i", "--csv", dest="csv",
                        help="Open a csv file by trying to import it", metavar="FILE")
    parser.add_option("-x", "--excel", dest="excel",
                        help="Import an excel file", metavar="FILE")
    parser.add_option("-t", "--test", dest="test",  action="store_true",
                        default=False, help="Run a basic test app")

    opts, remainder = parser.parse_args()
    if opts.test == True:
        app = TestApp()
    else:
        if opts.projfile != None:
            app = DataExplore(projfile=opts.projfile)
        elif opts.msgpack != None:
            app = DataExplore(msgpack=opts.msgpack)
        elif opts.csv != None:
            app = DataExplore()
            t = app.getCurrentTable()
            t.importCSV(opts.csv, dialog=True)
        elif opts.excel != None:
            app = DataExplore()
            app.importExcel(opts.excel)
        else:
            app = DataExplore()
    app.mainloop()

if __name__ == '__main__':
    main()