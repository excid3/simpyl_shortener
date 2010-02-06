# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from django import http
from django.template import Context, loader

from models import Option, Relation

def main(request):
    url = request.POST.get('url', '')
    type = request.POST.get('submit', '').lower()
    
    new_url = ''
    error = ''
    
    if type:
        if url.startswith('http://'):
            if type == 'shorten':
                # Get the current count from the database
                # This count keeps track of how many urls we have made
                # Increment this number and call make_url
                # Save it to the database and we are good to go
                try:
                    count_ref = Option.objects.get(title="count")
                except:
                    # No existing count so we must create it
                    count_ref = Option(title="count", value=0)
                    count_ref.save()
                    
                count_ref.value += 1
                count_ref.save()
                
                internal_url = make_url(count_ref.value)
                new_url = 'http://%s/%s' % (request.get_host(), 
                                            internal_url)
                r = Relation(internal_url=internal_url, external_url = url)
                r.save()
                
        else:
            error = "Invalid http url: %s" % url
    
    t = loader.get_template('index.html')
    c = Context({
        'new_url': new_url,
        'error': error,
    })
    
    return http.HttpResponse(t.render(c))

def fetch(request):
    url = request.META.get('PATH_INFO', '')[1:]
    
    try:
        p = Relation.objects.get(internal_url=url)
        return http.HttpResponseRedirect(p.external_url)
    except:
        t = loader.get_template('404.html')
        c = Context(locals())
        return http.HttpResponseNotFound(t.render(c))

###############################################################################

def make_url(count):
    charset = "01234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    base = len(charset)

    string = ''

    while count > 0:
        result = count % base
        string += charset[result]
        count = count / base

    return string
