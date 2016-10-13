from flask import Flask, render_template, redirect, url_for
from flask import request
from MacOpener import MacOpener
import re
from MacStore import MacStoreByCsv
from MacsOpener import MacsOpener
from RepeatTimer import RepeatTimer
import argparse

app = Flask(__name__)


@app.route('/', methods=['GET'])
def home():
    return render_template('index.html', error=request.args.get('error'))


@app.route('/', methods=['POST'])
def submit():
    mac = request.form.get('mac')
    isp = request.form.get('isp')
    save = 'save' in request.form

    if mac is None or len(mac) == 0 or isp is None:
        return redirect(url_for('home', error='MAC or isp is None'))

    if not isp.isalnum() or int(isp) > 3:
        return render_template('index.html', error='isp is incorrect')

    mac = mac.replace('-', ':').upper().strip()
    if not re.match('^([0-9a-fA-F]{2})(([:][0-9a-fA-F]{2}){5})$', mac):
        return render_template('index.html',
                               error='wrong format of MAC (should be HH:HH:HH:HH:HH:HH or HH-HH-HH-HH-HH-HH)')

    mac_opener.open(mac, int(isp))
    print(mac, isp)
    if save:
        mac_store.add_mac(mac, isp)
    return render_template('index.html')

    # html = '''<form action="/" method="post">
    #                 <label>mac</label>
    #                 <input name="mac" id="mac"/>
    #                 <select name="isp">
    #                     <option value="1">联通</option>
    #                     <option value="2">电信</option>
    #                     <option value="3">移动</option>
    #                 </select>
    #                 <input type="checkbox" id="save" name="save" value="save"/>
    #                 <label>save</label>
    #                 <button type="submit">ok</button>
    #             </form>'''
    # if request.method == 'GET':
    #     return html
    # elif request.method == 'POST':
    #     mac = request.form.get('mac')
    #     isp = request.form.get('isp')
    #     save = 'save' in request.form
    #
    #     if mac is None or len(mac) == 0 or isp is None:
    #         return html + '<label>error: MAC or isp is None</label>'
    #
    #     if not isp.isalnum() or int(isp) > 3:
    #         return html + '<label>error: isp</label>'
    #
    #     mac = mac.replace('-', ':').upper().strip()
    #     if not re.match('^([0-9a-fA-F]{2})(([:][0-9a-fA-F]{2}){5})$', mac):
    #         return html + '<label>wrong format of MAC (should be HH:HH:HH:HH:HH:HH or HH-HH-HH-HH-HH-HH)</label>'
    #
    #     mac_opener.open(mac, int(isp))
    #     print(mac, isp)
    #     if save:
    #         mac_store.add_mac(mac, isp)
    #     return html + 'ok!'

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='MAC opener for GUET by nightwind')

    parser.add_argument('-l', '--listen', default='0.0.0.0')
    parser.add_argument('-p', '--port', default=5000)
    parser.add_argument('-s', '--server', default='172.16.1.1')
    parser.add_argument('-sp', '--server port', dest='server_port', default=20015)
    parser.add_argument('-i', '--ip')
    parser.add_argument('-t', '--interval', default=5 * 60)
    parser.add_argument('-d', '--delay', default=0)
    args = parser.parse_args()

    try:
        mac_store = MacStoreByCsv()
        mac_opener = MacOpener(server=args.server, port=args.server_port, local_ip=args.ip)
        action = MacsOpener(mac_store, mac_opener)
        timer = RepeatTimer(args.interval, action.do, args.delay)
        timer.setDaemon(True)
        timer.start()
        app.run(args.listen, args.port)
    except AssertionError as e:
        print(e)
        exit(1)
