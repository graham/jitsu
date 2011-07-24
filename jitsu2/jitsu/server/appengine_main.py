import jitsu.server.response

class MainJitsuHandler(webapp.RequestHandler):
    def get(self):
        d = {}
        d['url'] = self.request.path_info
        d['environ'] = os.environ
        d['ip'] = self.request.remote_addr
        d['cookie_data'] = self.request.cookies
        d['raw_url'] = self.request.path_info+'?'+self.request.query_string
        d['body_file'] = self.request.body_file
    
        d['post_form_data'] = self.request.postvars
        d['request_type'] = 'GET'
        d['request_hostname'] = 'appspot.com'
        d['form_data'] = self.request.queryvars
        d['get_form_data'] = self.request.urlvars
    
        if (self.request.url.startswith('https')):
            d['secure'] = True
        else:
            d['secure'] = False
    
        d['server'] = ''
    
        r = jitsu.server.response.Response(**d)

        section = r.render()

        r.render_headers()
        self.do_write_headers()

        continue_after = False

        try:
            if types.GeneratorType == type(section):
                for i in section:
                    if type(i) == jitsu.server.runafter.RunAfter:
                        continue_after = i
                        break;
                    else:
                        self.response.out.write(str(i))
            else:
                self.response.out.write(str(section))
    
            self.response.out.wfile.flush()
            self.response.out.wfile.close()
            r.finish()
        except socket.error:
            print('ERROR: Client Disconnected before recving all information.')
        finally:
            pass

        if continue_after:
            self.server.job_list.append(section)


def main():
  application = webapp.WSGIApplication([
        ('.*', MainJitsuHandler)
    ],
                                       debug=True)
  wsgiref.handlers.CGIHandler().run(application)


if __name__ == '__main__':
  main()