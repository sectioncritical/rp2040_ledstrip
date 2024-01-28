import usb_midi
import usb_cdc
import supervisor

#import storage

#storage.disable_usb_drive()

supervisor.runtime.autoreload=False
usb_midi.disable()
usb_cdc.enable(console=True, data=True)
