<script setup>
import DefaultTheme from 'vitepress/theme'

const { Layout } = DefaultTheme
</script>

<template>
    <Layout>
        <template #home-hero-before>
            <div class="maiDecorationBg">
                <div class="background-layer"></div>
                <div class="pattern-layer"></div>
                <div class="shines-layer">
                    <div class="shines">
                        <div class="shine diamond-pink"></div>
                        <div class="shine diamond-yellow"></div>
                        <div class="shine diamond-white"></div>
                        <div class="shine star-white"></div>
                        <div class="shine star-yellow-left"></div>
                        <div class="shine star-yellow-right"></div>
                    </div>
                </div>
                <div class="decoration-container">
                    <div class="auroras">
                        <div class="aurora aurora-front"></div>
                        <div class="aurora aurora-back"></div>
                    </div>
                    <div class="clouds">
                        <div class="cloud front-left"></div>
                        <div class="cloud front-right"></div>
                        <div class="cloud front-center"></div>
                        <div class="cloud back-left"></div>
                        <div class="cloud back-right"></div>
                        <div class="cloud back-center"></div>
                    </div>
                    <div class="moon"></div>
                    <div class="shooting-stars">
                        <div class="shooting-star shooting-star1">
                            <div class="shooting-star-inner">
                                <div class="shooting-star-tail"></div>
                                <div class="shooting-star-head"></div>
                            </div>
                        </div>
                        <div class="shooting-star shooting-star2">
                            <div class="shooting-star-inner">
                                <div class="shooting-star-tail"></div>
                                <div class="shooting-star-head"></div>
                            </div>
                        </div>
                        <div class="shooting-star shooting-star3">
                            <div class="shooting-star-inner">
                                <div class="shooting-star-tail"></div>
                                <div class="shooting-star-head"></div>
                            </div>
                        </div>
                        <div class="shooting-star shooting-star4">
                            <div class="shooting-star-inner">
                                <div class="shooting-star-tail"></div>
                                <div class="shooting-star-head"></div>
                            </div>
                        </div>
                        <div class="shooting-star shooting-star5">
                            <div class="shooting-star-inner">
                                <div class="shooting-star-tail"></div>
                                <div class="shooting-star-head"></div>
                            </div>
                        </div>
                        <div class="shooting-star shooting-star6">
                            <div class="shooting-star-inner">
                                <div class="shooting-star-tail"></div>
                                <div class="shooting-star-head"></div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </template>
    </Layout>
</template>
<style scoped>
.background-layer,
.maiDecorationBg {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    z-index: -100;
}

.background-layer {
    background-size: cover;
    background-image: linear-gradient(0deg, #fff, #c1f7e1 40%, #7c81ff);
    animation: gradient 10s infinite linear;
}

@keyframes gradient {
    0% {
        background-position: 0 0;
    }

    50% {
        background-position: 0 100%;
    }

    to {
        background-position: 0 0;
    }
}

.pattern-layer {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-size: cover;
    z-index: -99;
    background-image: url(https://maimai.sega.jp/assets/maiDecorationBg/bg_pattern.png);
    background-repeat: repeat;
    background-position: 50%;
    background-size: 52px;
    mix-blend-mode: overlay;
    animation: pattern-layer 10s infinite linear;
}

@media screen and (max-width: 600px) {
    .pattern-layer {
        background-size: 26px;
    }
}

@keyframes pattern-layer {
    0% {
        background-position: 0 0;
    }

    to {
        background-position: -20% 20%;
    }
}

.shines-layer {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    z-index: 0;
    background-image: url(https://maimai.sega.jp/assets/maiDecorationBg/pc/bg_shines.png);
    background-size: 1332px;
    background-position: center 24px;
    background-repeat: repeat;
}

@media screen and (max-width: 600px) {
    .shines-layer {
        background-image: url(https://maimai.sega.jp/assets/maiDecorationBg/sp/bg_shines.png);
        background-size: 380px;
        background-position: center 28px;
    }
}

.shines {
    position: relative;
    width: 100%;
    height: 100%;
}

.shine {
    position: absolute;
    width: 20px;
    height: 20px;
    top: 0;
    left: 0;
    background-size: contain;
    background-repeat: no-repeat;
}

.shine.diamond-white {
    top: 256px;
    left: 1180px;
    background-image: url(https://maimai.sega.jp/assets/maiDecorationBg/shine/diamond_white.png);
    animation: diamond 3s infinite linear;
}

@media screen and (max-width: 600px) {
    .shine.diamond-white {
        top: 66px;
        left: 202px;
    }
}

.shine.diamond-pink {
    top: 32px;
    left: 324px;
    background-image: url(https://maimai.sega.jp/assets/maiDecorationBg/shine/diamond_pink.png);
    animation: diamond 3s infinite 1s linear;
}

@media screen and (max-width: 600px) {
    .shine.diamond-pink {
        width: 12px;
        height: 12px;
        top: 36px;
        left: 273px;
    }
}

.shine.diamond-yellow {
    top: 306px;
    left: 136px;
    background-image: url(https://maimai.sega.jp/assets/maiDecorationBg/shine/diamond_yellow.png);
    animation: diamond 3s infinite 2s linear;
}

@media screen and (max-width: 600px) {
    .shine.diamond-yellow {
        top: 26px;
        left: 298px;
    }
}

.shine.star-white {
    width: 30px;
    height: 30px;
    top: 230px;
    left: 552px;
    background-image: url(https://maimai.sega.jp/assets/maiDecorationBg/shine/star_white.png);
    opacity: 0;
    animation: star 3s infinite linear;
}

@media screen and (max-width: 600px) {
    .shine.star-white {
        top: 84px;
        left: 318px;
    }
}

.shine.star-yellow-left {
    top: 200px;
    left: 296px;
    top: 114px;
    left: 12px;
}

.shine.star-yellow-left,
.shine.star-yellow-right {
    width: 30px;
    height: 30px;
    background-image: url(https://maimai.sega.jp/assets/maiDecorationBg/shine/star_yellow.png);
    opacity: 0;
    animation: star 3s infinite 1s linear;
}

.shine.star-yellow-right {
    top: 404px;
    left: 1356px;
}

@media screen and (max-width: 600px) {
    .shine.star-yellow-right {
        top: 20px;
        left: 120px;
        background-image: url(https://maimai.sega.jp/assets/maiDecorationBg/shine/star_pink.png);
    }
}

@keyframes diamond {
    0% {
        transform: scaleX(1);
    }

    80% {
        transform: scaleX(1);
    }

    90% {
        transform: scaleX(0);
    }

    to {
        transform: scaleX(1);
    }
}

@keyframes star {
    0% {
        opacity: 0;
        transform: rotate(0);
    }

    20% {
        opacity: 1;
    }

    40% {
        opacity: 0;
        transform: rotate(1turn);
    }

    to {
        opacity: 0;
        transform: rotate(1turn);
    }
}

.auroras {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 246px;
    z-index: -1;
    background-image: url(https://maimai.sega.jp/assets/maiDecorationBg/pc/aurora.png);
    background-repeat: repeat-x;
    background-size: 3196px;
    background-position: 0 100%;
    animation: auroras 50s infinite linear;
}

@media screen and (max-width: 600px) {
    .auroras {
        background-image: url(https://maimai.sega.jp/assets/maiDecorationBg/sp/aurora.png);
        background-size: 1660px;
        background-position: left bottom 150px;
        animation: auroras 40s infinite linear;
    }
}

@keyframes auroras {
    0% {
        opacity: 1;
    }

    20% {
        opacity: 0.6;
    }

    80% {
        opacity: 0.6;
    }

    to {
        opacity: 1;
    }
}

.aurora {
    position: absolute;
    top: 0;
    left: 0;
    background-size: contain;
    background-repeat: no-repeat;
}

.aurora.aurora-front {
    top: -250px;
    left: 0;
    width: 200%;
    height: 473px;
    background-image: url(https://maimai.sega.jp/assets/maiDecorationBg/pc/aurora.png);
    background-repeat: repeat-x;
    opacity: 0;
    animation: aurora 120s infinite linear;
}

@media screen and (max-width: 600px) {
    .aurora.aurora-front {
        top: -66px;
        height: 168px;
        background-image: url(https://maimai.sega.jp/assets/maiDecorationBg/sp/aurora.png);
        background-repeat: repeat-x;
        animation: aurora 120s infinite linear;
    }
}

.aurora.aurora-back {
    top: -270px;
    left: 0;
    width: 200%;
    height: 168px;
    background-image: url(https://maimai.sega.jp/assets/maiDecorationBg/pc/aurora.png);
    background-repeat: repeat-x;
    opacity: 0;
    animation: aurora 90s infinite linear reverse;
}

@media screen and (max-width: 600px) {
    .aurora.aurora-back {
        top: -66px;
        height: 407px;
        background-image: url(https://maimai.sega.jp/assets/maiDecorationBg/sp/aurora.png);
        animation: aurora 90s infinite linear reverse;
    }
}

@keyframes aurora {
    0% {
        opacity: 0;
        transform: translateX(0);
    }

    1% {
        opacity: 0.8;
    }

    80% {
        opacity: 0.8;
    }

    99% {
        opacity: 0;
        transform: translateX(-100%);
    }

    to {
        opacity: 0;
        transform: translateX(0);
    }
}

.clouds {
    position: relative;
    width: 100%;
    height: 100%;
}

.cloud {
    position: absolute;
    top: 0;
    left: 0;
    background-size: contain;
    background-repeat: no-repeat;
}

.cloud.front-left {
    top: 370px;
    left: 104px;
    width: 297px;
    height: 141px;
    z-index: -97;
    background-image: url(https://maimai.sega.jp/assets/maiDecorationBg/pc/cloud/front_left.png);
    animation: cloud 18s infinite linear;
}

@media screen and (max-width: 600px) {
    .cloud.front-left {
        top: 268px;
        left: 18px;
        width: 148.5px;
        height: 70.5px;
    }
}

.cloud.front-center {
    top: 484px;
    left: 1020px;
    width: 255px;
    height: 122px;
    z-index: -97;
    background-image: url(https://maimai.sega.jp/assets/maiDecorationBg/pc/cloud/front_center.png);
    animation: cloud 19s infinite linear;
}

@media screen and (max-width: 600px) {
    .cloud.front-center {
        top: 360px;
        left: 236px;
        width: 127.5px;
        height: 61px;
    }
}

.cloud.front-right {
    top: 231px;
    left: 1152px;
    width: 356px;
    height: 164px;
    z-index: -97;
    background-image: url(https://maimai.sega.jp/assets/maiDecorationBg/pc/cloud/front_right.png);
    animation: cloud 20s infinite linear;
}

@media screen and (max-width: 600px) {
    .cloud.front-right {
        top: 146px;
        left: 266px;
        width: 178px;
        height: 82px;
    }
}

.cloud.back-left {
    top: 236px;
    left: -58px;
    width: 507px;
    height: 265px;
    z-index: -98;
    background-image: url(https://maimai.sega.jp/assets/maiDecorationBg/pc/cloud/back_left.png);
    animation: cloud 12s infinite linear;
}

@media screen and (max-width: 600px) {
    .cloud.back-left {
        top: 2px;
        left: -82px;
        width: 253.5px;
        height: 132.5px;
    }
}

.cloud.back-center {
    top: 410px;
    left: 1140px;
    width: 231px;
    height: 150px;
    z-index: -98;
    background-image: url(https://maimai.sega.jp/assets/maiDecorationBg/pc/cloud/back_center.png);
    animation: cloud 13s infinite linear;
}

@media screen and (max-width: 600px) {
    .cloud.back-center {
        top: 324px;
        left: 300px;
        width: 115.5px;
        height: 75px;
    }
}

.cloud.back-right {
    top: 164px;
    left: 1000px;
    width: 371px;
    height: 194px;
    z-index: -98;
    background-image: url(https://maimai.sega.jp/assets/maiDecorationBg/pc/cloud/back_right.png);
    animation: cloud 14s infinite linear;
}

@media screen and (max-width: 600px) {
    .cloud.back-right {
        top: 114 px;
        left: 192px;
        width: 185.5px;
        height: 97px;
    }
}

@keyframes cloud {
    0% {
        opacity: 0;
        transform: translateX(0);
    }

    20% {
        opacity: 1;
    }

    80% {
        opacity: 1;
    }

    90% {
        opacity: 0;
        transform: translateX(100%);
    }

    to {
        opacity: 0;
        transform: translateX(0);
    }
}

.moon {
    position: absolute;
    top: 0;
    left: 20px;
    width: 198px;
    height: 198px;
    z-index: 1;
    background-size: contain;
    background-repeat: no-repeat;
    background-image: url(https://maimai.sega.jp/assets/maiDecorationBg/moon.png);
    animation: moon 6s infinite linear alternate;
}

@media screen and (max-width: 600px) {
    .moon {
        top: 16px;
        left: 16px;
        width: 99px;
        height: 99px;
        animation: none;
    }
}

@keyframes moon {
    0% {
        transform: rotate(0);
    }

    to {
        transform: rotate(30deg);
    }
}

.shooting-stars {
    position: relative;
    width: 100%;
    height: 100%;
}

.shooting-star {
    position: absolute;
    top: 0;
    left: 0;
    z-index: -96;
    width: 308px;
    height: 308px;
    animation: shooting-star 2s infinite linear;
    opacity: 0;
}

@keyframes shooting-star {
    0% {
        transform: translateX(0) translateY(0);
        opacity: 0;
    }

    20% {
        opacity: 1;
    }

    40% {
        opacity: 1;
    }

    60% {
        transform: translateX(-100%) translateY(100%);
        opacity: 0;
    }

    to {
        transform: translateX(0) translateY(0);
        opacity: 0;
    }
}

.shooting-star.shooting-star1 {
    width: 154px;
    height: 154px;
    top: 81px;
    left: 147px;
}

@media screen and (max-width: 600px) {
    .shooting-star.shooting-star1 {
        width: 77px;
        height: 77px;
        top: -46px;
        left: 16px;
    }
}

.shooting-star.shooting-star2 {
    width: 154px;
    height: 154px;
    top: 74px;
    left: 486px;
    animation: shooting-star 2s infinite 0.8s linear;
}

@media screen and (max-width: 600px) {
    .shooting-star.shooting-star2 {
        width: 77px;
        height: 77px;
        top: -44px;
        left: 352px;
    }
}

.shooting-star.shooting-star3 {
    width: 308px;
    height: 308px;
    top: 20px;
    left: 436px;
}

@media screen and (max-width: 600px) {
    .shooting-star.shooting-star3 {
        width: 154px;
        height: 154px;
        top: 46px;
        left: 36px;
    }
}

.shooting-star.shooting-star4 {
    width: 154px;
    height: 154px;
    top: 12px;
    left: 1402px;
    animation: shooting-star 2s infinite 1s linear;
}

.shooting-star.shooting-star5 {
    width: 232px;
    height: 232px;
    top: 256px;
    left: 1160px;
    animation: shooting-star 2s infinite 0.8s linear;
}

@media screen and (max-width: 600px) {
    .shooting-star.shooting-star5 {
        display: none;
    }
}

.shooting-star.shooting-star6 {
    width: 154px;
    height: 154px;
    top: 304px;
    left: 1230px;
    animation: shooting-star 2s infinite 1s linear;
}

@media screen and (max-width: 600px) {
    .shooting-star.shooting-star6 {
        display: none;
    }
}

.shooting-star-inner {
    position: relative;
    width: 100%;
    height: 100%;
}

.shooting-star-head {
    position: absolute;
    bottom: 0;
    left: 0;
    width: 14%;
    height: 14%;
    background-image: url(https://maimai.sega.jp/assets/maiDecorationBg/shooting_star/head.png);
    background-size: contain;
    background-repeat: no-repeat;
    transform-origin: 50% 50%;
    animation: shooting-star-head 2.2s infinite linear;
}

@keyframes shooting-star-head {
    0% {
        transform: rotate(0deg);
    }

    to {
        transform: rotate(-1turn);
    }
}

.shooting-star-tail {
    top: 0;
    right: 0;
    width: 91%;
    height: 91%;
    background-image: url(https://maimai.sega.jp/assets/maiDecorationBg/shooting_star/tail.png);
    background-size: contain;
}

.rainbow,
.shooting-star-tail {
    position: absolute;
    background-repeat: no-repeat;
}

.rainbow {
    bottom: 140px;
    width: 100%;
    height: 399px;
    background-image: url(https://maimai.sega.jp/assets/maiDecorationBg/rainbow.png);
    background-size: 763px 399px;
    background-position: 50%;
    -webkit-clip-path: polygon(0 0, 0 0, 0 100%, 0 100%);
    clip-path: polygon(0 0, 0 0, 0 100%, 0 100%);
    animation: rainbow 2s ease forwards;
}

@media screen and (max-width: 600px) {
    .rainbow {
        bottom: 176px;
        background-image: url(https://maimai.sega.jp/assets/maiDecorationBg/sp/rainbow.png);
        background-size: 390px 268px;
    }
}

@keyframes rainbow {
    0% {
        -webkit-clip-path: polygon(0 0, 0 0, 0 100%, 0 100%);
        clip-path: polygon(0 0, 0 0, 0 100%, 0 100%);
        transform: scale(0.8);
    }

    to {
        -webkit-clip-path: polygon(0 0, 100% 0, 100% 100%, 0 100%);
        clip-path: polygon(0 0, 100% 0, 100% 100%, 0 100%);
        transform: scale(1);
    }
}

.rainbow-bottom {
    position: absolute;
    bottom: 40px;
    width: 100%;
    height: 230px;
    background-image: url(https://maimai.sega.jp/assets/maiDecorationBg/pc/cloud/rainbow_bottom.png);
    background-size: 1380px 230px;
    background-repeat: no-repeat;
    background-position: 50%;
    animation: rainbow-bottom 2s ease forwards;
}

@media screen and (max-width: 600px) {
    .rainbow-bottom {
        bottom: 140px;
        background-image: url(https://maimai.sega.jp/assets/maiDecorationBg/sp/rainbow_bottom.png);
        background-size: 400px 108px;
    }
}

@keyframes rainbow-bottom {
    0% {
        transform: scale(0.8);
    }

    to {
        transform: scale(1);
    }
}
</style>