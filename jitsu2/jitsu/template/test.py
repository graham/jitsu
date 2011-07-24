import jitsu.template.tml

x = jitsu.template.tml.Template(open('jitsu/template/template.html').read())

print(x.render())