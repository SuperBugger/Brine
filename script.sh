#!/bin/bash

sudo apt-get update

sudo apt-get install -y salt-master salt-minion python3-pyqt5 python3-paramiko python3-yaml


local_ip="0.0.0.0"


sudo sed -i "s/#master: salt/master: $local_ip #brine/g" /etc/salt/minion

sudo sed -i "s/#master: salt/master: $local_ip #brine/g" /etc/salt/master
sudo sed -i '/^#interface:/s/^#//' /etc/salt/master

sudo mkdir -p /srv/salt/brine/
sudo mkdir -p /srv/salt/brine/templates/

cat > /srv/salt/brine/check_sources_list.sls <<EOL
install_packages_based_on_osnova_linux_onyx:
  cmd.run:
    - name: |
        if grep -q '^#.*OSNova Linux onyx' /etc/apt/sources.list; then
          apt-get install -y {{ pillar['packages'] }}
        elif grep -q 'OSNova Linux onyx' /etc/apt/sources.list; then
          if blkid | grep -q onyx; then
            apt-get install -y {{ pillar['packages'] }}
          else
            echo "Вставьте диск меткой «OSNova Linux onyx - amd64 DVD disk1» и повторите попытку."
          fi
        fi
    - shell: /bin/bash
EOL

cat > /srv/salt/brine/common-password.sls <<EOL
{% set minlen = pillar.get('minlen', '') %}
{% set minclass = pillar.get('minclass', '') %}
{% set minrepeat = pillar.get('minrepeat', '') %}
{% set maxrepeat = pillar.get('maxrepeat', '') %}
{% set difok = pillar.get('difok', '') %}

update-common-password:
  file.managed:
    - name: /etc/pam.d/common-password
    - source: salt://brine/templates/common-password.jinja
    - template: jinja
    - context:
        minlen: {{ minlen }}
        minclass: {{ minclass }}
        minrepeat: {{ minrepeat }}
        maxrepeat: {{ maxrepeat }}
        difok: {{ difok }}
EOL

cat > /srv/salt/brine/templates/common-password.jinja <<EOL
common-password.jinja

{% if minlen != '--' %}
minlen={{ minlen }}
{% endif %}
{% if minclass != '--' %}
minclass={{ minclass }}
{% endif %}
{% if minrepeat != '--' %}
minrepeat={{ minrepeat }}
{% endif %}
{% if maxrepeat != '--' %}
maxrepeat={{ maxrepeat }}
{% endif %}
{% if difok != '--' %}
difok={{ difok }}
{% endif %}
EOL


cat > /srv/salt/brine/delete_system_temp_files.sls <<EOL
delete_temp_files:
  cmd.run:
    - name: |
        find /tmp -type f -delete
        find /var/tmp -type f -delete

cleanup_tmp:
  file.absent:
    - name: /tmp/*
    - onchanges:
      - cmd: delete_temp_files

cleanup_var_tmp:
  file.absent:
    - name: /var/tmp/*
    - onchanges:
      - cmd: delete_temp_files
EOL

cat > /srv/salt/brine/delete_user_temp_files.sls <<EOL
delete_user_cache_and_temp:
  cmd.run:
    - name: |
        find /home/{{ pillar['username'] }}/.cache -type f -delete
        find /home/{{ pillar['username'] }}/.cache -type d -exec rm -r {} \;
        find /home/{{ pillar['username'] }}/tmp -type f -delete
        find /home/{{ pillar['username'] }}/tmp -type d -exec rm -r {} \;
    - require:
      - user_exists

user_exists:
  user.present:
    - name: {{ pillar['username'] }}
EOL

cat > /srv/salt/brine/list_sessions.sls <<EOL
list_sessions:
  cmd.run:
    - name: loginctl list-sessions
EOL

cat > /srv/salt/brine/onyx_repo.sls <<EOL
check_and_clone_sources_list_main:
  cmd.run:
    - name: |
        if [ ! -f "/etc/apt/sources.list.d/onyx:dl.nppct.ru.list" ]; then
          sudo wget "https://dl.nppct.ru/onyx/stable/misc/apt/sources.list.d/onyx:dl.nppct.ru.list" \
            -P "/etc/apt/sources.list.d/"
        fi

{% if pillar.get('with_devel', False) %}
check_and_clone_sources_list_devel:
  cmd.run:
    - name: |
        if [ ! -f "/etc/apt/sources.list.d/onyx-devel:dl.nppct.ru.list" ]; then
          sudo wget "https://dl.nppct.ru/onyx/stable/misc/apt/sources.list.d/onyx-devel:dl.nppct.ru.list" \
            -P "/etc/apt/sources.list.d/"
        fi

check_and_clone_sources_list_devel_update:
  cmd.run:
    - name: |
        if [ ! -f "/etc/apt/sources.list.d/onyx-devel-update:dl.nppct.ru.list" ]; then
          sudo wget "https://dl.nppct.ru/onyx/stable/misc/apt/sources.list.d/onyx-devel-update:dl.nppct.ru.list" \
            -P "/etc/apt/sources.list.d/"
        fi
{% endif %}

check_and_clone_sources_list_update:
  cmd.run:
    - name: |
        if [ ! -f "/etc/apt/sources.list.d/onyx-update:dl.nppct.ru.list" ]; then
          sudo wget "https://dl.nppct.ru/onyx/stable/misc/apt/sources.list.d/onyx-update:dl.nppct.ru.list" \
            -P "/etc/apt/sources.list.d/"
        fi

check_and_clone_auth_conf:
  cmd.run:
    - name: |
        if [ ! -f "/etc/apt/auth.conf.d/dl.nppct.ru.conf" ]; then
          sudo wget "https://dl.nppct.ru/onyx/stable/misc/apt/auth.conf.d/dl.nppct.ru.conf" \
            -O "/etc/apt/auth.conf.d/dl.nppct.ru.conf"
        fi

replace_login_password:
  cmd.run:
    - name: |
        sudo sed -i "s/login [^ ]*/login {{pillar.get('login','')}}/" "/etc/apt/auth.conf.d/dl.nppct.ru.conf"
        sudo sed -i "s/password [^ ]*/password {{pillar.get('password','')}}/" "/etc/apt/auth.conf.d/dl.nppct.ru.conf"

comment_cdrom_source:
  cmd.run:
    - name: |
        sudo sed -i '/^deb cdrom:/ s/^/#/' "/etc/apt/sources.list"

EOL

cat > /srv/salt/brine/repo.sls << 'EOF'
{% set lines_to_remove = pillar.get('lines_to_remove', []) %}

{% for line in lines_to_remove %}
remove_line_{{ loop.index }}_from_sources_list:
  file.line:
    - name: /etc/apt/sources.list
    - mode: delete
    - content: '{{ line }}'
    - match: '^{{ line }}$'

remove_line_{{ loop.index }}_from_sources_list_d_files:
  cmd.run:
    - name: |
        for file in /etc/apt/sources.list.d/*; do
          line_num=$(grep -n "{{ line }}" "$file" | cut -d: -f1)
          if [ ! -z "$line_num" ]; then
            sed -i "${line_num}d" "$file"
          fi
        done
    - require:
      - file: remove_line_{{ loop.index }}_from_sources_list
{% endfor %}

remove_files_with_no_words_in_sources_list_d:
  cmd.run:
    - name: |
        for file in /etc/apt/sources.list.d/*; do
          if [ $(wc -w <"$file") -eq 0 ]; then
            rm "$file"
          fi
        done
    - require:
      {% for line in lines_to_remove %}
      - cmd: remove_line_{{ loop.index }}_from_sources_list_d_files
      {% endfor %}

check_for_nppct_files_and_remove_auth_conf:
  cmd.run:
    - name: |
        if [ -z "$(find /etc/apt/sources.list.d/ -type f -name '*nppct*' -print -quit)" ]; then
          rm -f /etc/apt/auth.conf.d/dl.nppct.ru.conf
        fi
    - require:
      - cmd: remove_files_with_no_words_in_sources_list_d

EOF

cat > /srv/salt/brine/pic.sls <<EOL
detect_kde_plasma:
  cmd.run:
    - name: 'ps -e | grep -q -E "plasmashell|startkde"'
    - stateful: true

detect_lxqt:
  cmd.run:
    - name: 'ps -e | grep -q -E "lxqt-session"'
    - stateful: true


copy_file:                                                                            
  module.run:                                                                         
    - name: cp.get_file                                                               
    - path: salt://{{pillar.get("pic_filename", "")}}                                 
    - dest: /usr/share/wallpapers/{{pillar.get("pic_filename", "")}}


set_wallpaper_kde:
  cmd.run:
    - name: |
        qdbus org.kde.plasmashell /PlasmaShell org.kde.PlasmaShell.evaluateScript "
          var Desktops = desktops();                                                  
          for (i=0;i<Desktops.length;i++) {                                           
            var d = Desktops[i];                                                      
            d.wallpaperPlugin = 'org.kde.image';                                      
            d.currentConfigGroup = Array('Wallpaper', 'org.kde.image', 'General');    
            d.writeConfig('Image', 'file:///usr/share/wallpapers/{{pillar.get("pic_filename", "")}}')
          }"
    - runas: {{pillar.get("username", "")}}
    - shell: /bin/bash


set_wallpaper_lxqt:
  cmd.run:
    - name: |
        export DISPLAY=:0
        pcmanfm-qt --set-wallpaper=/usr/share/wallpapers/{{pillar.get("pic_filename", "")}}
    - runas: {{pillar.get("username", "")}}
EOL

cat > /srv/salt/brine/screenlock.sls <<EOL
{% set turn = salt['pillar.get']('turn', '') %}
{% set time_value = salt['pillar.get']('time_value', '') %}
{% set time_in_seconds = time_value | int * 60 %}

check_environment:
  cmd.run:
    - name: |
        if ps -e | grep -q -E "plasmashell|startkde"; then
          for userhome in /home/*; do
            if [ -d "\$userhome/.config" ]; then
              kwriteconfig --file \$userhome/.config/kscreenlockerrc --group Daemon --key Autolock {{ turn }}
              kwriteconfig --file \$userhome/.config/kscreenlockerrc --group Daemon --key Timeout {{ time_value }}
            fi
          done
        elif ps -e | grep -q -E "lxqt-session"; then
          for userhome in /home/*; do
            if [ -d "\$userhome/.config/lxqt" ]; then
              sed -i "s/^enableIdlenessWatcher=.*/enableIdlenessWatcher={{ turn }}/" \$userhome/.config/lxqt/lxqt-powermanagement.conf
              sed -i "s/^idlenessTimeSecs=.*/idlenessTimeSecs={{ time_in_seconds }}/" \$userhome/.config/lxqt/lxqt-powermanagement.conf
            fi
          done
        fi
    - unless: test -z "\$(ps -e | grep -E 'plasmashell|startkde|lxqt-session')"
EOL

cat > /srv/salt/brine/timetable.sls <<EOL
blocl_sessions_schedule:
  schedule.present:
    - name: block_sessions
    - function: cmd.run
    - job_args:
      - loginctl lock-sessions
    - when:
      - Monday {{pillar.get("monday", "")}}
      - Tuesday {{pillar.get("tuesday", "")}}
      - Wednesday {{pillar.get("wednesday", "")}}
      - Thursday {{pillar.get("thursday", "")}}
      - Friday {{pillar.get("friday", "")}}
      - Saturday {{pillar.get("saturday", "")}}
      - Sunday {{pillar.get("sunday", "")}}

EOL

cat > /srv/salt/brine/usb_rules.sls <<EOL
create_usb_rules:
  file.managed:
    - name: /etc/udev/rules.d/99-usb-brine.rules
    - contents: |
        ENV{ID_USB_DRIVER}=="usb-storage",ENV{UDISKS_IGNORE}="{{pillar.get("turn", "")}}"
    - makedirs: True

reload_udev_rules:
  cmd.run:
    - name: udevadm control --reload-rules
    - onchanges:
      - file: create_usb_rules

grepusbrules:                                                                                                                                                                                                                          
  cmd.run:                                                                                                                                                                                                                                  
    - name: grep -q 'ENV{ID_USB_DRIVER}=="usb-storage",ENV{UDISKS_IGNORE}="{{pillar.get("turn", "")}}"' /etc/udev/rules.d/99-usb-brine.rules && echo "Ограничена работа usb" || echo "Работа не ограничена usb"
EOL


echo "Установка и настройка завершены."
