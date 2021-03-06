from torch import nn


class CBR(nn.Module):
    def __init__(self, ch0, ch1, bn=True, sample='down', activation=nn.ReLU(True), dropout=False):
        super().__init__()
        self.bn = bn
        self.activation = activation
        self.dropout = dropout
        if sample == 'down':
            self.c = nn.Conv2d(ch0, ch1, 3, 1, 1)
        else:
            self.c = nn.ConvTranspose2d(ch0, ch1, 3, 1, 1)
        if bn:
            self.batchnorm = nn.BatchNorm2d(ch1, affine=True)
        if dropout:
            self.Dropout = nn.Dropout()

    def forward(self, x):
        h = self.c(x)
        if self.bn:
            h = self.batchnorm(h)
        if self.dropout:
            h = self.Dropout(h)
        if not self.activation is None:
            h = self.activation(h)
        return h


class ResBlock(nn.Module):
    def __init__(self, ch0, ch1, bn=True, sample='down', activation=nn.ReLU(True)):
        super().__init__()
        self.conv_block = nn.Sequential(
            nn.Conv2d(ch0, ch1, 3, 1, 1) if sample == 'down' else nn.ConvTranspose2d(ch0, ch1, 3, 1, 1),
            nn.BatchNorm2d(ch1, affine=True),
            activation,
            nn.Dropout(0.5),
            nn.Conv2d(ch0, ch1, 3, 1, 1) if sample == 'down' else nn.ConvTranspose2d(ch0, ch1, 3, 1, 1),
            nn.BatchNorm2d(ch1, affine=True),
            activation,
            nn.Dropout(0.5),
            nn.Conv2d(ch0, ch1, 3, 1, 1) if sample == 'down' else nn.ConvTranspose2d(ch0, ch1, 3, 1, 1),
            nn.BatchNorm2d(ch1, affine=True),
            activation,
        )

    def forward(self, x):
        return x + self.conv_block(x)


class UpSamplePixelShuffle(nn.Module):
    def __init__(self, in_ch, out_ch, up_scale=2, activation=nn.ReLU(True)):
        super().__init__()
        self.activation = activation

        self.c = nn.Conv2d(in_channels=in_ch,
                           out_channels=out_ch * up_scale * up_scale,
                           kernel_size=3,
                           stride=1,
                           padding=1,
                           bias=False)
        self.ps = nn.PixelShuffle(up_scale)

    def forward(self, x):
        h = self.c(x)
        h = self.ps(h)
        if not self.activation is None:
            h = self.activation(h)
        return h


def weights_init(m):
    classname = m.__class__.__name__
    if classname.find('Conv') != -1:
        m.weight.data.normal_(0.0, 0.02)
    elif classname.find('BatchNorm2d') != -1 or classname.find('InstanceNorm2d') != -1:
        m.weight.data.normal_(1.0, 0.02)
        m.bias.data.fill_(0)
