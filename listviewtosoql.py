import os
import xml.etree.ElementTree as etree

class ListViewToSOQL(object):

    def convertSObjectViews( self, sobj_name, listview_paths ):
        print( '\tconverting listview xml to SOQL-like text for '+ sobj_name )

        for lvp in listview_paths:
            # eventual file contents
            f_lines = []
            f_dirname = os.path.dirname('.')

            root = etree.parse( lvp ).getroot()
            xmlns="{http://soap.sforce.com/2006/04/metadata}"
            lv_name = root.find( xmlns+'fullName' ).text
            f_lines.append( r'//'+lv_name+'\n' )

            filter = root.find( xmlns +'booleanFilter')
            filter_logic = ''
            if filter != None :
                filter_logic =filter.text.replace("'",'')
                f_lines.append( r'//'+ filter_logic +'\n' )
            
            ctext = []
            cols = root.findall( xmlns+'columns' )
            for c in cols:
                ctext.append(c.text)
            fields = 'SELECT ' + ','.join( c.replace("'",'') for c in ctext) + '\n\t FROM '+ sobj_name

            fs = []
            opsToSymbols = {    'equals' : '=', 'notEqual':'!=', 
                                'greaterThan':'>', 'lessThan':'<', 
                                'contains':'IN', 'notContain':'NOT IN', 
                                'lessOrEqual':'<=', 'greaterOrEqual':'>='}

            filters = root.findall(xmlns+'filters')
            filter_list = []
            wheres = ''
            if( filters != None ):
                for f in filters:
                    try:
                        field = f.find(xmlns+'field').text.replace("'",'')
                    except:
                        field = ''

                    try:
                        op = f.find(xmlns+'operation').text.replace("'",'')
                        op = opsToSymbols[op]
                    except:
                        op = ''

                    try:
                        value = f.find(xmlns+'value').text.replace("'",'')
                    except:
                        value = ''
                    wheres += '\n\t' + field +' '+ op +' ' + value
            
            query_str = ''
            if len(wheres) > 0:
                query_str = fields +'\n WHERE \n' + wheres
            else:
                query_str = fields

            f_lines.append( query_str )

            # now write the results to local 'objectDictionary' folder
            # we print to console
            dest_dir = os.path.join( f_dirname,'objectDictionary\\'+sobj_name)
            dest_file = lv_name+".soql"

            try:
                os.makedirs( dest_dir )
            except:
                pass # dir already exists
            f_path = os.path.join( dest_dir, dest_file )
            f = open( f_path, "w")
            f.writelines( f_lines )
            f.close()


    def findObjectsWithViews(self):
        # need to get the object name from furth up the folder path ( see above root def )
        # ...\objects\<object name>\listViews\<listViewName>
        objectsFolder = '..\\force-app\\main\\default\\objects'
        objectDirs = os.walk( objectsFolder )

        # top level from \objects
        toplevel = objectDirs.next()

        # just the subdirs of the objects dir from toplevel
        allobjects = toplevel[1]

        for sobjName in allobjects:
            objxdirs = os.walk(objectsFolder+'\\'+sobjName).next()[1]
            # print ( objxdirs )
            lvpaths = []
            if( 'listViews' in objxdirs ):
                print( sobjName + ' has list views')

                for lvpath, lvdirs,lvfiles in os.walk(objectsFolder+'\\'+sobjName +'\\listViews'):
                    for fname in lvfiles:
                        lvpaths.append( os.path.join( lvpath, fname) )
            else:
                print( sobjName + ' has no list views ')
            # send that objects list of listview file paths to be processed
            if len( lvpaths ) > 0:
                self.convertSObjectViews(sobjName, lvpaths)

lv = ListViewToSOQL()
lv.findObjectsWithViews()