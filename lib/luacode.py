#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2015-2016 Peter Magnusson <peter@birchroad.net>


# these functions are needed on the device, otherwise they will be
# uploaded during prepare
LUA_FUNCTIONS = ['recv_block', 'recv_name','recv','shafile', 'send_block', 'send_file']

DOWNLOAD_FILE = "file.open('{filename}') print(file.seek('end', 0)) file.seek('set', {bytes_read}) uart.write(0, file.read({chunk_size}))file.close()"

PRINT_FILE = "file.open('{filename}') print('---{filename}---') print(file.read()) file.close() print('---')"

LIST_FILES = 'for key,value in pairs(file.list()) do print(key,value) end'

RECV_LUA = \
r"""
function recv_block(d)
  if string.byte(d, 1) == 1 then
    size = string.byte(d, 2)
    uart.write(0,'\006')
    if size > 0 then
      file.write(string.sub(d, 3, 3+size-1))
    else
      file.close()
      uart.on('data')
      uart.setup(0,{baud},8,0,1,1)
    end
  else
    uart.write(0, '\021' .. d)
    uart.setup(0,{baud},8,0,1,1)
    uart.on('data')
  end
end
function recv_name(d) d = string.gsub(d, '\000', '') file.remove(d) file.open(d, 'w') uart.on('data', 130, recv_block, 0) uart.write(0, '\006') end
function recv() uart.setup(0,{baud},8,0,1,0) uart.on('data', '\000', recv_name, 0) uart.write(0, 'C') end
function shafile(f) file.open(f, "r") print(crypto.toHex(crypto.hash("sha1",file.read()))) file.close() end
"""

SEND_LUA = \
r"""
function send_block(d) l = string.len(d) uart.write(0, '\001' + string.char(l) + string.rep(' ', 128 - l)) return l end
function send_file(f) file.open(f) s=file.seek('end', 0) p=0 while (p<s) do file.seek('set',p) p=p+send_block(file.read(128)) end send_block('') file.close() end
"""

UART_SETUP = 'uart.setup(0,{baud},8,0,1,1)'
