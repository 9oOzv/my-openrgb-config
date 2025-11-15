from hsluv import hsluv_to_rgb
from openrgb import OpenRGBClient
from openrgb.utils import RGBColor, DeviceType
from time import time, sleep
from dataclasses import dataclass


brightness = 0.1

client = OpenRGBClient()
devices = client.devices
for d in devices:
    d.set_mode("direct")


drams = [
    d
    for d in devices
    if d.type == DeviceType.DRAM
]

rest = [
    d
    for d in devices
    if d.type != DeviceType.DRAM
]


@dataclass
class GradientPoint:
    phase: float
    h: int
    s: int
    l: int  # noqa: E741


gradient = [
    GradientPoint(0.00, 160, 100, 20),
    GradientPoint(0.30, 160, 100, 20),
    GradientPoint(0.50, 360, 100, 20),
    GradientPoint(0.80, 360, 100, 20),
]

dram_gradient = [
    GradientPoint(0.00, 250, 100, 20),
    GradientPoint(0.30, 250, 100, 20),
    GradientPoint(0.50, 360, 100, 20),
    GradientPoint(0.80, 360, 100, 20),
]

parts = [
    (drams, dram_gradient, 0.5),
    (rest, gradient, 1.0)
]


def interpolate(
    a: tuple[int, ...],
    b: tuple[int, ...],
    t: float,
) -> tuple[int, ...]:
    return tuple(
        a[i] * (1 - t) + b[i] * t
        for i in range(len(a))
    )


def interpolate_gradient(
    gradient: list[GradientPoint],
    phase: float,
) -> tuple[float, float, float]:
    phase = phase % 1
    n = len(gradient)
    if n == 1:
        return gradient[0]
    for i in range(n - 1):
        if gradient[i].phase <= phase <= gradient[i + 1].phase:
            break
    gp1 = gradient[i]
    gp2 = gradient[i + 1]
    j = (phase - gp1.phase) / (gp2.phase - gp1.phase)
    return interpolate(
        (
            gradient[i].h,
            gradient[i].s,
            gradient[i].l
        ),
        (
            gradient[i + 1].h,
            gradient[i + 1].s,
            gradient[i + 1].l
        ),
        j
    )


def color(
    gradient: list[GradientPoint],
    phase: float,
) -> RGBColor:
    hsluv = interpolate_gradient(gradient, phase)
    hsluv = (
        hsluv[0],
        hsluv[1],
        brightness * hsluv[2],
    )
    rgb = [
        int(255 * x)
        for x in hsluv_to_rgb(hsluv)
    ]
    return RGBColor(*rgb)


def colors(
    gradient: list[tuple[float, ...]],
    n: int,
    f: float = 1,
) -> list[RGBColor]:
    return [
        color(gradient, time() / 1200 + i / n * f)
        for i in range(n)
    ]


while True:
    for devices, gradient, f in parts:
        num_leds = [
            len(d.leds)
            for d in devices
        ]
        colors_ = colors(gradient, sum(num_leds), f)
        for d, n in zip(devices, num_leds):
            d.set_colors(colors_[:n])
            colors_ = colors_[n:]
            sleep(0.2)
