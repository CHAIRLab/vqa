
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.autograd import Variable

use_cuda = torch.cuda.is_available()


def SeperableConv2d(in_channels, out_channels, kernel_size=1, stride=1, padding=0, onnx_compatible=False):
    """Replace Conv2d with a depthwise Conv2d and Pointwise Conv2d.
    """
    ReLU = nn.ReLU if onnx_compatible else nn.ReLU6
    return nn.Sequential(
        nn.Conv2d(in_channels=in_channels, out_channels=in_channels, kernel_size=kernel_size,
               groups=in_channels, stride=stride, padding=padding),
        nn.BatchNorm2d(in_channels),
        nn.ReLU(),
        nn.Conv2d(in_channels=in_channels, out_channels=out_channels, kernel_size=1),
    )

class InvertedResidual(nn.Module):
    def __init__(self, inp, oup, stride, expand_ratio, use_batch_norm=True, onnx_compatible=False):
        super(InvertedResidual, self).__init__()
        ReLU = nn.ReLU if onnx_compatible else nn.ReLU6

        self.stride = stride
        assert stride in [1, 2]

        hidden_dim = round(inp * expand_ratio)
        self.use_res_connect = self.stride == 1 and inp == oup

        if expand_ratio == 1:
            if use_batch_norm:
                self.conv = nn.Sequential(
                    # dw
                    nn.Conv2d(hidden_dim, hidden_dim, 3, stride, 1, groups=hidden_dim, bias=False),
                    nn.BatchNorm2d(hidden_dim),
                    ReLU(inplace=True),
                    # pw-linear
                    nn.Conv2d(hidden_dim, oup, 1, 1, 0, bias=False),
                    nn.BatchNorm2d(oup),
                )
            else:
                self.conv = nn.Sequential(
                    # dw
                    nn.Conv2d(hidden_dim, hidden_dim, 3, stride, 1, groups=hidden_dim, bias=False),
                    ReLU(inplace=True),
                    # pw-linear
                    nn.Conv2d(hidden_dim, oup, 1, 1, 0, bias=False),
                )
        else:
            if use_batch_norm:
                self.conv = nn.Sequential(
                    # pw
                    nn.Conv2d(inp, hidden_dim, 1, 1, 0, bias=False),
                    nn.BatchNorm2d(hidden_dim),
                    ReLU(inplace=True),
                    # dw
                    nn.Conv2d(hidden_dim, hidden_dim, 3, stride, 1, groups=hidden_dim, bias=False),
                    nn.BatchNorm2d(hidden_dim),
                    ReLU(inplace=True),
                    # pw-linear
                    nn.Conv2d(hidden_dim, oup, 1, 1, 0, bias=False),
                    nn.BatchNorm2d(oup),
                )
            else:
                self.conv = nn.Sequential(
                    # pw
                    nn.Conv2d(inp, hidden_dim, 1, 1, 0, bias=False),
                    ReLU(inplace=True),
                    # dw
                    nn.Conv2d(hidden_dim, hidden_dim, 3, stride, 1, groups=hidden_dim, bias=False),
                    ReLU(inplace=True),
                    # pw-linear
                    nn.Conv2d(hidden_dim, oup, 1, 1, 0, bias=False),
                )

    def forward(self, x):
        if self.use_res_connect:
            return x + self.conv(x)
        else:
            return self.conv(x)

class SoccerModule(nn.Module):
    # SoccerModule
    '''
    # Load Pre-train SoccerModule Please Refer pre-train folder
    # Debug Usage
    '''
    def __init__(self, image_dim, text_dim, map_dim):
        super(SoccerModule,self).__init__()
        self.map_dim = map_dim
        self.conv1 = nn.Conv2d(image_dim,map_dim,kernel_size=1)
        self.conv2 = nn.Conv2d(map_dim, 1, kernel_size=1)
        self.textfc = nn.Linear(text_dim,map_dim)
        self.tau = 1
        self.alpha = 0.92

    def forward(self, tau, alpha, input_image_feat, input_text, input_image_attention1=None, input_image_attention2=None):
        image_mapped = self.conv1(input_image_feat)  #(N, map_dim, H, W)
        text_mapped = self.textfc(input_text).view(-1, self.map_dim,1,1).expand_as(image_mapped)
        elmtwize_mult = image_mapped * text_mapped
        elmtwize_mult = F.normalize(elmtwize_mult, p=2, dim=1) #(N, map_dim, H, W)
        att_grid = self.conv2(elmtwize_mult) #(N, 1, H, W)
        tau += self.tau
        alpha += self.alpha
        return att_grid, tau, alpha

class ContourModule(nn.Module):
    # ContourModule
    '''
    # Load Pre-train ContourModule
    # Debug Usage
    '''
    def __init__(self, image_dim, text_dim, map_dim):
        super(ContourModule,self).__init__()
        self.map_dim = map_dim
        self.conv1 = nn.Conv2d(image_dim,map_dim,kernel_size=1)
        self.conv2 = nn.Conv2d(map_dim, 1, kernel_size=1)
        self.textfc = nn.Linear(text_dim,map_dim)
        # self.lc_out = nn.Linear(map_dim, self.out_num_choice)
        self.tau = 1
        self.alpha = 0.71

    def forward(self, tau, alpha, input_image_feat, input_text, input_image_attention1=None, input_image_attention2=None):
        image_mapped = self.conv1(input_image_feat)  #(N, map_dim, H, W)
        text_mapped = self.textfc(input_text).view(-1, self.map_dim,1,1).expand_as(image_mapped)
        elmtwize_mult = image_mapped * text_mapped
        elmtwize_mult = F.normalize(elmtwize_mult, p=2, dim=1) #(N, map_dim, H, W)
        att_grid = self.conv2(elmtwize_mult) #(N, 1, H, W)
        # scores = self.lc_out(att_grid) For scene graph generation usage
        tau += self.tau
        alpha += self.alpha
        return att_grid, tau, alpha


class ColorModule(nn.Module):
    # Color

    '''
    # Load Pre-train Color Bolb Detector
    # Debug Usage
    '''
    def __init__(self, output_num_choice, image_dim, text_dim, map_dim):
        super(ColorModule,self).__init__()
        self.out_num_choice = output_num_choice
        self.image_dim = image_dim
        self.text_fc = nn.Linear(text_dim, map_dim)
        self.att_fc_1 = nn.Linear(image_dim, map_dim)
        self.lc_out = nn.Linear(map_dim, self.out_num_choice)
        self.tau = 1
        self.alpha = 1

    def forward(self, tau, alpha, input_image_feat, input_text, input_image_attention1=None, input_image_attention2=None):
        H, W = input_image_attention1.shape[2:4]
        att_softmax_1 = F.softmax(input_image_attention1.view(-1, H * W),dim=1).view(-1, 1, H*W)
        image_reshape = input_image_feat.view(-1,self.image_dim,H * W) #[N,image_dim,H*W]
        att_feat_1 = torch.sum(att_softmax_1 * image_reshape, dim=2)    #[N, image_dim]
        att_feat_1_mapped = self.att_fc_1(att_feat_1)       #[N, map_dim]

        text_mapped = self.text_fc(input_text)
        elmtwize_mult = att_feat_1_mapped * text_mapped  #[N, map_dim]
        elmtwize_mult = F.normalize(elmtwize_mult, p=2, dim=1)
        scores = self.lc_out(elmtwize_mult)
        tau += self.tau
        alpha += self.alpha
        return scores, tau, alpha

class TransformModule(nn.Module):
    def __init__(self, image_dim, text_dim, map_dim,kernel_size=5, padding=2):
        super(TransformModule,self).__init__()
        self.map_dim = map_dim
        self.conv1 = nn.Conv2d(1, map_dim, kernel_size=kernel_size, padding=padding)
        self.conv2 = nn.Conv2d(map_dim, 1, kernel_size=1)
        self.textfc = nn.Linear(text_dim,map_dim)
        self.tau = 1
        self.alpha = 1

    def forward(self, tau, alpha, input_image_feat, input_text, input_image_attention1=None, input_image_attention2=None):
        image_att_mapped = self.conv1(input_image_attention1)  #(N, map_dim, H, W)
        text_mapped = self.textfc(input_text).view(-1, self.map_dim,1,1).expand_as(image_att_mapped)
        elmtwize_mult = image_att_mapped * text_mapped
        elmtwize_mult = F.normalize(elmtwize_mult, p=2, dim=1) #(N, map_dim, H, W)
        att_grid = self.conv2(elmtwize_mult) #(N, 1, H, W)
        tau += self.tau
        alpha += self.alpha
        return att_grid, tau, alpha

class Person1Module(nn.Module):
    def __init__(self, image_dim, text_dim, map_dim):
        super(Person1Module,self).__init__()
        self.map_dim = map_dim
        self.conv1 = nn.Conv2d(image_dim,map_dim,kernel_size=1)
        self.conv2 = nn.Conv2d(map_dim, 1, kernel_size=1)
        self.textfc = nn.Linear(text_dim,map_dim)
        self.tau = 1
        self.alpha = 0.56
        
    def forward(self, tau, alpha, input_image_feat, input_text, input_image_attention1=None, input_image_attention2=None):
        image_mapped = self.conv1(input_image_feat)  #(N, map_dim, H, W)
        text_mapped = self.textfc(input_text).view(-1, self.map_dim,1,1).expand_as(image_mapped)
        elmtwize_mult = image_mapped * text_mapped
        elmtwize_mult = F.normalize(elmtwize_mult, p=2, dim=1) #(N, map_dim, H, W)
        att_grid = self.conv2(elmtwize_mult) #(N, 1, H, W)
        tau += self.tau
        alpha += self.alpha
        return att_grid, tau, alpha

class Person2Module(nn.Module):
    def __init__(self, image_dim, text_dim, map_dim):
        super(Person2Module,self).__init__()
        self.map_dim = map_dim
        self.conv = nn.Sequential(nn.Conv2d(image_dim,map_dim,kernel_size=1), nn.Conv2d(map_dim,map_dim,kernel_size=1),
                                  nn.Conv2d(map_dim, map_dim, kernel_size=1), nn.Conv2d(map_dim,map_dim,kernel_size=1),
                                  nn.Conv2d(map_dim, map_dim, kernel_size=1), nn.Conv2d(map_dim,map_dim,kernel_size=1),
                                  nn.Conv2d(map_dim, map_dim, kernel_size=1), nn.Conv2d(map_dim,map_dim,kernel_size=1))
        self.conv2 = nn.Conv2d(map_dim, 1, kernel_size=1)
        self.textfc = nn.Linear(text_dim, map_dim)
        self.tau = 2
        self.alpha = 0.62

    def forward(self, tau, alpha, input_image_feat, input_text, input_image_attention1=None, input_image_attention2=None):
        image_mapped = self.conv(input_image_feat)  # (N, map_dim, H, W)
        text_mapped = self.textfc(input_text).view(-1, self.map_dim, 1, 1).expand_as(image_mapped)
        elmtwize_mult = image_mapped * text_mapped
        elmtwize_mult = F.normalize(elmtwize_mult, p=2, dim=1)  # (N, map_dim, H, W)
        att_grid = self.conv2(elmtwize_mult)  # (N, 1, H, W)
        tau += self.tau
        alpha += self.alpha
        return att_grid, tau, alpha

class Person3Module(nn.Module):
    def __init__(self, image_dim, text_dim, map_dim):
        super(Person3Module,self).__init__()
        self.map_dim = map_dim
        self.conv = nn.Sequential(SeperableConv2d(image_dim, map_dim), SeperableConv2d(map_dim, map_dim),
                                  SeperableConv2d(map_dim, map_dim),SeperableConv2d(map_dim, map_dim),
                                  SeperableConv2d(map_dim, map_dim), SeperableConv2d(map_dim, map_dim),
                                  SeperableConv2d(map_dim, map_dim), SeperableConv2d(map_dim, map_dim),)
        self.conv2 = nn.Conv2d(map_dim, 1, kernel_size=1)
        self.textfc = nn.Linear(text_dim, map_dim)
        self.tau = 2.5
        self.alpha = 0.71

    def forward(self, tau, alpha, input_image_feat, input_text, input_image_attention1=None, input_image_attention2=None):
        image_mapped = self.conv(input_image_feat)  # (N, map_dim, H, W)
        text_mapped = self.textfc(input_text).view(-1, self.map_dim, 1, 1).expand_as(image_mapped)
        elmtwize_mult = image_mapped * text_mapped
        elmtwize_mult = F.normalize(elmtwize_mult, p=2, dim=1)  # (N, map_dim, H, W)
        att_grid = self.conv2(elmtwize_mult)  # (N, 1, H, W)
        tau += self.tau
        alpha += self.alpha
        return att_grid, tau, alpha

class ExistModule(nn.Module):
    def __init__(self,output_num_choice, image_height, image_width):
        super(ExistModule,self).__init__()
        self.out_num_choice = output_num_choice
        self.lc_out = nn.Linear(image_height*image_width + 3, self.out_num_choice)
        self.tau = 1
        self.alpha = 1

    def forward(self, tau, alpha, input_image_feat, input_text, input_image_attention1=None, input_image_attention2=None):
        H, W = input_image_attention1.shape[2:4]
        att_all = input_image_attention1.view(-1, H*W) ##flatten attention to [N, H*W]
        att_avg = torch.mean(att_all, 1, keepdim=True)
        att_min = torch.min(att_all, 1, keepdim=True)[0]
        att_max = torch.max(att_all, 1, keepdim=True)[0]
        att_concat = torch.cat((att_all, att_avg, att_min, att_max), 1)
        scores = self.lc_out(att_concat)
        tau += self.tau
        alpha += self.alpha
        return scores, tau, alpha

class DirectionModule(nn.Module):
    def __init__(self, output_num_choice, image_dim, text_dim, map_dim):
        super(DirectionModule,self).__init__()
        self.out_num_choice = output_num_choice
        self.image_dim = image_dim
        self.text_fc = nn.Linear(text_dim, map_dim)
        self.att_fc_1 = nn.Linear(image_dim, map_dim)
        self.lc_out = nn.Linear(map_dim, self.out_num_choice)
        self.tau = 1.1
        self.alpha = 1
        
    def forward(self, tau, alpha, input_image_feat, input_text, input_image_attention1=None, input_image_attention2=None):
        H, W = input_image_attention1.shape[2:4]
        att_softmax_1 = F.softmax(input_image_attention1.view(-1, H * W),dim=1).view(-1, 1, H*W)
        image_reshape = input_image_feat.view(-1,self.image_dim,H * W) #[N,image_dim,H*W]
        att_feat_1 = torch.sum(att_softmax_1 * image_reshape, dim=2)    #[N, image_dim]
        att_feat_1_mapped = self.att_fc_1(att_feat_1)       #[N, map_dim]

        text_mapped = self.text_fc(input_text)
        elmtwize_mult = att_feat_1_mapped * text_mapped  #[N, map_dim]
        elmtwize_mult = F.normalize(elmtwize_mult, p=2, dim=1)
        scores = self.lc_out(elmtwize_mult)
        tau += self.tau
        alpha += self.alpha
        return scores, tau, alpha

class Rel1Module(nn.Module):
    def __init__(self, Person1Module, SceneModule):
        super(Rel1Module,self).__init__()
        self.personModule = Person1Module
        self.sceneModule = SceneModule
        self.tau = 1
        self.alpha = 1
    def forward(self, tau, alpha, input_image_feat, input_text, input_image_attention1=None, input_image_attention2=None):
        find_result, tau, alpha = self.personModule(tau, alpha, input_image_feat,input_text,input_image_attention1,input_image_attention2)
        att_grid, tau, alpha = self.sceneModule(tau, alpha, input_image_feat,input_text,input_image_attention1,find_result)
        tau += self.tau
        alpha += self.alpha
        return att_grid, tau, alpha

class Rel2Module(nn.Module):
    def __init__(self, Person2Module, SceneModule):
        super(Rel2Module,self).__init__()
        self.personModule = Person2Module
        self.sceneModule = SceneModule
        self.tau = 1
        self.alpha = 1
    def forward(self, tau, alpha, input_image_feat, input_text, input_image_attention1=None, input_image_attention2=None):
        find_result, tau, alpha = self.personModule(tau, alpha, input_image_feat,input_text,input_image_attention1,input_image_attention2)
        att_grid, tau, alpha = self.sceneModule(tau, alpha, input_image_feat,input_text,input_image_attention1,find_result)
        tau += self.tau
        alpha += self.alpha
        return att_grid, tau, alpha

class Rel3Module(nn.Module):
    def __init__(self, Person3Module, SceneModule):
        super(Rel3Module,self).__init__()
        self.personModule = Person3Module
        self.sceneModule = SceneModule
        self.tau = 1
        self.alpha = 1
    def forward(self, tau, alpha, input_image_feat, input_text, input_image_attention1=None, input_image_attention2=None):
        find_result, tau, alpha = self.personModule(tau, alpha, input_image_feat,input_text,input_image_attention1,input_image_attention2)
        att_grid, tau, alpha = self.sceneModule(tau, alpha, input_image_feat,input_text,input_image_attention1,find_result)
        tau += self.tau
        alpha += self.alpha
        return att_grid, tau, alpha

class Rel4Module(nn.Module):
    def __init__(self, Person4Module, SceneModule):
        super(Rel4Module,self).__init__()
        self.personModule = Person4Module
        self.sceneModule = SceneModule
        self.tau = 1
        self.alpha = 1
    def forward(self, tau, alpha, input_image_feat, input_text, input_image_attention1=None, input_image_attention2=None):
        find_result, tau, alpha = self.personModule(tau, alpha, input_image_feat,input_text,input_image_attention1,input_image_attention2)
        att_grid, tau, alpha = self.sceneModule(tau, alpha, input_image_feat,input_text,input_image_attention1,find_result)
        tau += self.tau
        alpha += self.alpha
        return att_grid, tau, alpha

class StatusModule(nn.Module):
    def __init__(self, output_num_choice, image_dim, text_dim, map_dim):
        super(StatusModule, self).__init__()
        self.out_num_choice = output_num_choice
        self.image_dim = image_dim
        self.text_fc = nn.Linear(text_dim, map_dim)
        self.att_fc_1 = nn.Linear(image_dim, map_dim)
        self.lc_out = nn.Linear(map_dim, self.out_num_choice)
        self.tau = 1.1
        self.alpha = 1

    def forward(self, tau, alpha, input_image_feat, input_text, input_image_attention1=None,
                input_image_attention2=None):
        H, W = input_image_attention1.shape[2:4]
        att_softmax_1 = F.softmax(input_image_attention1.view(-1, H * W), dim=1).view(-1, 1, H * W)
        image_reshape = input_image_feat.view(-1, self.image_dim, H * W)  # [N,image_dim,H*W]
        att_feat_1 = torch.sum(att_softmax_1 * image_reshape, dim=2)  # [N, image_dim]
        att_feat_1_mapped = self.att_fc_1(att_feat_1)  # [N, map_dim]

        text_mapped = self.text_fc(input_text)
        elmtwize_mult = att_feat_1_mapped * text_mapped  # [N, map_dim]
        elmtwize_mult = F.normalize(elmtwize_mult, p=2, dim=1)
        scores = self.lc_out(elmtwize_mult)
        tau += self.tau
        alpha += self.alpha
        return scores, tau, alpha

class Person4Module(nn.Module):
    def __init__(self, image_dim, text_dim, map_dim):
        super(Person4Module,self).__init__()
        self.map_dim = map_dim
        self.conv = nn.Sequential(nn.Conv2d(image_dim,map_dim,kernel_size=1), nn.Conv2d(map_dim,map_dim,kernel_size=1),
                                  nn.Conv2d(map_dim, map_dim, kernel_size=1), nn.Conv2d(map_dim,map_dim,kernel_size=1),
                                  nn.Conv2d(map_dim, map_dim, kernel_size=1), nn.Conv2d(map_dim, map_dim, kernel_size=1),
                                  InvertedResidual(map_dim, map_dim, stride=1, expand_ratio=0.2), InvertedResidual(map_dim, map_dim, stride=1, expand_ratio=0.2),)
        self.conv2 = nn.Conv2d(map_dim, 1, kernel_size=1)
        self.textfc = nn.Linear(text_dim, map_dim)
        self.tau = 2.9
        self.alpha = 0.88

    def forward(self, tau, alpha, input_image_feat, input_text, input_image_attention1=None, input_image_attention2=None):
        image_mapped = self.conv(input_image_feat)  # (N, map_dim, H, W)
        text_mapped = self.textfc(input_text).view(-1, self.map_dim, 1, 1).expand_as(image_mapped)
        elmtwize_mult = image_mapped * text_mapped
        elmtwize_mult = F.normalize(elmtwize_mult, p=2, dim=1)  # (N, map_dim, H, W)
        att_grid = self.conv2(elmtwize_mult)  # (N, 1, H, W)
        tau += self.tau
        alpha += self.alpha
        return att_grid, tau, alpha

class SceneModule(nn.Module):
    def __init__(self,):
        super(SceneModule,self).__init__()
        self.tau = 1
        self.alpha = 1
    def forward(self, tau, alpha, input_image_feat, input_text, input_image_attention1=None, input_image_attention2=None):
        N, _, H, W = input_image_feat.shape
        res = torch.ones((N, 1, H, W))
        att_grid = Variable(res)
        att_grid = att_grid.cuda() if use_cuda else att_grid
        tau += self.tau
        alpha += self.alpha
        return att_grid, tau, alpha

class CountModule(nn.Module):
    def __init__(self,output_num_choice, image_height, image_width):
        super(CountModule,self).__init__()
        self.out_num_choice = output_num_choice
        self.lc_out = nn.Linear(image_height*image_width + 3, self.out_num_choice)
        self.tau = 1
        self.alpha = 1
    def forward(self, tau, alpha, input_image_feat, input_text, input_image_attention1=None, input_image_attention2=None):
        H, W = input_image_attention1.shape[2:4]
        att_all = input_image_attention1.view(-1, H*W) ##flatten attention to [N, H*W]
        att_avg = torch.mean(att_all, 1, keepdim=True)
        att_min = torch.min(att_all, 1, keepdim=True)[0]
        att_max = torch.max(att_all,1, keepdim=True)[0]
        att_concat = torch.cat((att_all, att_avg, att_min, att_max), 1)
        scores = self.lc_out(att_concat)
        tau += self.tau
        alpha += self.alpha
        return scores, tau, alpha

# To do
# Add more network modules

