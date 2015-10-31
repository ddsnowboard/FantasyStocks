import sys
from urllib import request, parse
# This is just a test of the Google Closure Compiler API. I was going to use it 
# for all my JavaScript to make it smaller. It's only in this folder because 
# this is where all my JavaScript is. 

with open(sys.argv[1]) as f:
    print(request.urlopen("http://closure-compiler.appspot.com/compile", parse.urlencode([
        ("js_code", f.read()), 
        ("compilation_level", "ADVANCED_OPTIMIZATIONS"), 
        ('language', "ECMASCRIPT5"),
        ("output_format", "text"),
        ("output_info", "compiled_code")]).encode("UTF-8")).read())
