from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import cgi

from database_setup import Store, Base, Tv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///tvcatalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

class webServerHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        try:
            if self.path.endswith("/stores/new"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                output = ""
                output += "<html><body>"
                output += "<h1>Make New Store</h1>"
                output += "<form method = 'POST' enctype='multipart/form-data' action = '/stores/new'>"
                output += "<input name = 'newStoreName' type = 'text' placeholder = 'New Store Name' > "
                output += "<input type='submit' value='Create'>"
                output += "</form></html></body>"
                self.wfile.write(output)
                return
            
            if self.path.endswith("/edit"):
                storeIDPath = self.path.split("/")[2]
                myStoreQuery = session.query(Store).filter_by(
                    id=storeIDPath).one()
                if myStoreQuery:
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    output = "<html><body>"
                    output += "<h1>"
                    output += myStoreQuery.name
                    output += "</h1>"
                    output += "<form method='POST' enctype='multipart/form-data' action = '/stores/%s/edit' >" % storeIDPath
                    output += "<input name = 'newStoreName' type='text' placeholder = '%s' >" % myStoreQuery.name
                    output += "<input type = 'submit' value = 'Rename'>"
                    output += "</form>"
                    output += "</body></html>"

                    self.wfile.write(output)

            if self.path.endswith("/delete"):
                storeIDPath = self.path.split("/")[2]

                myStoreQuery = session.query(Store).filter_by(
                    id=storeIDPath).one()
                if myStoreQuery:
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    output = ""
                    output += "<html><body>"
                    output += "<h1>Are you sure you want to delete %s?" % myStoreQuery.name
                    output += "<form method='POST' enctype = 'multipart/form-data' action = '/stores/%s/delete'>" % storeIDPath
                    output += "<input type = 'submit' value = 'Delete'>"
                    output += "</form>"
                    output += "</body></html>"

                    self.wfile.write(output)

            if self.path.endswith("/stores"):
                stores = session.query(Store).all()
                output = ""
                output += "<a href = '/stores/new' > Make New Store Here </a></br></br>"

                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                output += "<html><body>"
                for store in stores:
                    output += store.name
                    output += "</br>"
                    output += "<a href ='/stores/%s/edit' >Edit </a> " % store.id
                    output += "</br>"
                    output += "<a href ='/stores/%s/delete'> Delete </a>" % store.id
                    output += "</br></br></br>"

                output += "</body></html>"
                self.wfile.write(output)
                return

        except IOError:
            self.send_error(404, 'File Not Found: %s' % self.path)


    def do_POST(self):
        try:
            if self.path.endswith("/delete"):
                storeIDPath = self.path.split("/")[2]
                myStoreQuery = session.query(Store).filter_by(
                    id=storeIDPath).first()
                if myStoreQuery != []:
                    session.delete(myStoreQuery)
                    session.commit()
                    self.send_response(301)
                    self.send_header('Content-type', 'text/html')
                    self.send_header('Location', '/stores')
                    self.end_headers()

            if self.path.endswith("/edit"):
                ctype, pdict = cgi.parse_header(
                    self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                messagecontent = fields.get('newTvName')
                storeIDPath = self.path.split("/")[2]

                myStoreQuery = session.query(Store).filter_by(
                    id=storeIDPath).one()
                if myStoreQuery != []:
                    myStoreQuery.name = messagecontent[0]
                    session.add(myStoreQuery)
                    session.commit()
                    self.send_response(301)
                    self.send_header('Content-type', 'text/html')
                    self.send_header('Location', '/stores')
                    self.end_headers()

            if self.path.endswith("/stores/new"):
                ctype, pdict = cgi.parse_header(
                    self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    messagecontent = fields.get('newStoreName')

                    # Create new Store Object
                    newStore = Store(name=messagecontent[0])
                    session.add(newStore)
                    session.commit()

                    self.send_response(301)
                    self.send_header('Content-type', 'text/html')
                    self.send_header('Location', '/stores')
                    self.end_headers()

        except:
            pass

def main():
    try:
        port = 8080
        server = HTTPServer(('', port), webServerHandler)
        print ('Web server running on port %s' % port)
        server.serve_forever()

    except KeyboardInterrupt:
        print ("^C received, shutting down server")
        server.socket.close()



if __name__ == '__main__':
    main()

