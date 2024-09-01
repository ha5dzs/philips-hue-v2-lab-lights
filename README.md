# Lab lights with the Philips Hue system with the Hue V2 CLIP API (i.e. the 'new' one)

I like decent lights. As someone involved in vision science and knowing what a decent light is, I find bad colour rendering, flickering and off-white colours annoying in a workplace and/or lab environment. Just like with monitors, most people that I know of tends to save a buck or two on devices that are supposed to work with humans. This comes at a cost of increased fatigue and low productivity. Following this logic, I bit the bullet and bought some Philips Hue lights. I found that all the applications are geared towards home automation and entertainment. These lights can be so much more. Each of these have an RGBwWcW array, and it seems that the colour mixing in RGB mode is working reasonably well.

But, Philips being Philips, they:

* Had an initial insecure and not-so-well-thought-out API
* Then they 'killed' that API
* They added a new API that nobody (as far as I know) uses and includes breaking changes from the old API
* ...and because of a presumed public uproar, they kept the old 'V1' amd the new 'V2' APIs working alongside each other, which complicates things
* Now Philips lights are not even Philips lights, but it still says Philips on the box. Classic.

So understandably this became a mess, and I didn't see any recent (as of, 2024) projects with these lights.

## Why

 I don't care about the home automation stuff. I especially don't want to connect any home automation stuff to the Internet. I don't want to change light parameters every millisecond to music, but I do, ever so desperately want to occasionally change the colour and to dim all my lights together in a controlled and precise manner. I have a bunch of these lights and I also want them to display the same chromaticity and luminance output that I set. I also want them to be wide spectrum so I can see what I am doing at my desk.

 Apparently that is too much to ask and (again, as far as I know) nobody did such a thing, so I read the docs and created this Python script.

## How does it work?

 The initial assumption is that the Hue system is properly set up with the usual tools. If it works with the Hue app (through the Hue Bridge, and not Bluetooth!), it will work with this code as well. It doesn't matter if you assign them to a 'scene' or 'room' or 'group' or what type you set them up as, or what you named them.

Initially, you'll need to press the button on the Hue Bridge to create your key. This is saved as a json file. Then, the code gets your lights, and logs the IDs. For each light it sets to `xy' mode, tosses your chromaticity coordinates and intensity percentage, and that's it. The lights are in xy mode, so they are prepared for all sorts of renderable chromaticities. This ensures that all the LEDs are used. The actual mixing of LED intensities within the light source ('bulb', or 'lamp', you get the idea) is not controlled by this script, but rather, it is controlled by the internal MCU inside each light source.

 If you are able to and need to, verify the chromaticity outputs with a suitable optical instrument.

 Since the 'new' API uses https and other goodies, there is a rate limit of 10 requests per second for setting each light. If you have a large number of lights, this will manifest as a scrolling effect as the new settings will be uploaded to each light.

 If there is a problem and something stops working, then try deleting the json files. If you get connectivity issues, try checking whether the Hue Bridge is still on the same local IP address, and that the IP address of the Hue Bridge matches with what is inside the Python script.

### Usage

 The following command in your terminal makes all your lights go D65, with all the luminance output they can do.

```sh
    python lablight.py 0.31272 0.32903 100
```

The first and second arguments are the CIE 1931 chromaticity coordinates, and the third argument is the intensity in percent [0 ... 100%].

If you don't specify any of these input arguments or you try to do something silly such as giving impossible colours, the code will set your lights to these above values. You will get an error message in the console. If the error message comes from the script, it will be clear and straightforward, if it comes from the light system, you will get a json object and you have to manually process it. The code sets the lights so that the last values are set are used as defaults when they are power-cycled. So, next time you turn these on, they will be exactly the same how you set them.

**note**: There are some sanity checks and error management in the code, but it is not entirely foolproof. There are better and more user-friendly solutions for end-users. I just got upset that I couldn't calibrate these lights easily and threw in about 10 hours of work (of reading, some programming, testing, and documenting and admittedly some swearing about what happened to 'let's make things better') to make this.

## How to start from scratch

 Install the Hue Bridge, connect it to your local network, install the Hue app, connect your lights. Verify that you can control your lights as they should be controlled.

 The code needs some Python libraries. These can be installed with the line below, just in case they are not already installed:

```sh
    pip install urllib3 requests
```

 To use this code, you will need the IP address of your bridge. By default, it looks for DHCP, so the IP address will be assigned by your router. You can use [nmap](https://nmap.org/download.html) or [arp](https://en.wikipedia.org/wiki/Address_Resolution_Protocol) to find it, or you can use [this tool written by Philips that runs in your browser](https://discovery.meethue.com/) to find the IP address of your Hue Bridge.

 **Change the IP address in the Python script so it would point to your own Hue Bridge!**

 This is pretty much all you need, now you can start using it.

## Chromaticity replication accuracy tests and results

All my lights are the 800-lumen 'White and colour ambinance' of 'Gamut type C' which is probably the latest (2016 onwards) one.

The primaries are:

| Colour | Chromaticity (x;y) |
|--------|---------------|
| Red | `0.6915; 0.3083` |
| Green | `0.17; 0.7` |
| Blue | `0.1532; 0.0475` |

The following was measured with a Sekonic C800 chromameter. The lights were driven at 100% intensity, the instrument's rotatable diffuser was set to 'High', and it was directly in very close proximity of the body of the light. Several (4-5) measurements were taken for the same condition, there was no significant measurement between the measured values, so I did not include the raw data. As this instrument measures illumination and not light output, the intensity values are omitted.

| Easy-to-remember name | Colour temperature | Chromaticity (x; y) as set | Chromaticity (x; y) as measured | Calculated colour temperature |
|-----------------------|--------------------|------------------------|-----------------------------|-------------------------------|
| Equal Energy | N/A | `0.33; 0.33` | `0.3274; 0.3255` | N/A |
| Incandescent | 2700K | `0.45986; 0.41060` | `0.4633; 0.4095` | 2644K |
| Warm white | 4000K | `0.38044; 0.37675` | `0.3819; 0.3780` | 3969K |
| D65 (The default one) | 6500K | `0.31272; 0.32903` | `0.3106; 0.3253` | 6651K |
| D76 (Cool white) | 7600K | `0.29924; 0.30911` | `0.2977; 0.3120` | 7657K |

## A little bit of waffle at the end (discussion, conclusion, whatever)

Perceptually, all the primary colours are deep and beautiful, and there was no observable difference in intensity and colour between light sources. The green one is the best one I have seen from a commercially available light. In literally every condition, I could see from the spectrum that the onboard MCU does its best to provide with a wide-spectrum light, at the desired chromaticity, with distinct peaks at the primary colours in the traditional blue-chip-illuminates-some-phosphor-type spectrum. I am even inclined to think that the slight difference between colour temperatures are originated from the limited measurement accuracy of the C800 chromameter. If I get really curious or hit an anomaly, I'll repeat these mesurements in a much more controlled environment and with a much more expensive (Minolta CS-150) device.

I also noticed that the Hue app and this Python script can mutually control these lights. Not only that, but it is possible to save a 'scene' created with the Phyton script, in the Hue app. So, once the desired illumination settings are set, it is possible to recall them in the Hue app without using this Python script, and presumably even cycle across them with a Zigbee remote.

So, anyway, if you are on a low budget, and you don't have the time to make and calibrate RGB lights yourself from scratch, these lights can be a reasonable compromise for illuminating your environment.

That being said, I only have these 800-lumen 'White and colour ambiance' E27 lights, so I don't know if other Philips Hue products will work the same way.
