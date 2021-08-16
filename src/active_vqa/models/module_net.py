import torch
import torch.nn as nn
import torch.nn.functional as F
from models.modules import *
from torch.autograd import Variable


use_cuda = torch.cuda.is_available()



class module_net(nn.Module):

    ##initiate all small modules which will be used here
    def __init__(self, image_height, image_width, in_image_dim, in_text_dim, out_num_choices, map_dim):
        super(module_net,self).__init__()
        self.image_height = image_height
        self.image_width = image_width
        self.in_image_dim = in_image_dim
        self.in_text_dim = in_text_dim
        self.out_num_choices = out_num_choices
        self.map_dim = map_dim
        self.SceneModule = SceneModule()
        self.SoccerModule = SoccerModule(image_dim=self.in_image_dim, text_dim=self.in_text_dim, map_dim=self.map_dim)
        self.ContourModule = ContourModule(image_dim=self.in_image_dim, text_dim=self.in_text_dim, map_dim=self.map_dim)
        self.Person1Module = Person1Module(image_dim=self.in_image_dim, text_dim=self.in_text_dim, map_dim=self.map_dim)
        self.Person2Module = Person2Module(image_dim=self.in_image_dim, text_dim=self.in_text_dim, map_dim=self.map_dim)
        self.Person3Module = Person3Module(image_dim=self.in_image_dim, text_dim=self.in_text_dim, map_dim=self.map_dim)
        self.Person4Module = Person4Module(image_dim=self.in_image_dim, text_dim=self.in_text_dim, map_dim=self.map_dim)
        self.TransformModule = TransformModule(image_dim=in_image_dim, text_dim=in_text_dim, map_dim=self.map_dim)
        self.Rel1Module = Rel1Module(Person1Module=self.Person1Module, SceneModule=self.SceneModule)
        self.Rel2Module = Rel2Module(Person2Module=self.Person2Module, SceneModule=self.SceneModule)
        self.Rel3Module = Rel3Module(Person3Module=self.Person3Module, SceneModule=self.SceneModule)
        self.Rel4Module = Rel4Module(Person4Module=self.Person4Module, SceneModule=self.SceneModule)
        self.CountModule = CountModule(output_num_choice=out_num_choices,
                                       image_height=image_height, image_width= image_width)
        self.ExistModule = ExistModule(output_num_choice=out_num_choices,
                                       image_height=image_height, image_width= image_width)
        self.ColorModule = ColorModule(output_num_choice=out_num_choices,
                                       image_dim=self.in_image_dim, text_dim=self.in_text_dim, map_dim=self.map_dim)
        self.DirectionModule = DirectionModule(output_num_choice=out_num_choices,
                                               image_dim=self.in_image_dim, text_dim=self.in_text_dim, map_dim=self.map_dim)
        self.StatusModule = StatusModule(output_num_choice=out_num_choices,
                                         image_dim=self.in_image_dim, text_dim=self.in_text_dim, map_dim=self.map_dim)
        self.layout2module = {
            '_Scene': self.SceneModule,
            '_Soccer': self.SoccerModule,
            '_Contour': self.ContourModule,
            '_Person1': self.Person1Module,
            '_Person2': self.Person2Module,
            '_Person3': self.Person3Module,
            '_Person4': self.Person4Module,
            '_Rel1': self.Rel1Module,
            '_Rel2': self.Rel12Module,
            '_Rel3': self.Rel13Module,
            '_Rel4': self.Rel14Module,
            '_Status': self.StatusModule,
            '_Transform': self.TransformModule,
            '_Count': self.CountModule,
            '_Exist': self.ExistModule,
            '_Color': self.ColorModule,
            '_Direction': self.DirectionModule,
        }

    #text[N, D_text]

    def recursively_assemble_network(self, tau, alpha, input_image_variable, input_text_attention_variable, expr_list):
        current_module = self.layout2module[expr_list['module']]
        time_idx = expr_list['time_idx']
        text_index = Variable(torch.LongTensor([time_idx]))
        text_index = text_index.cuda() if use_cuda else text_index
        text_at_time = torch.index_select(input_text_attention_variable, dim=1,
                                          index=text_index).view(-1, self.in_text_dim)

        input_0 = None
        input_1 = None
        tau = 0
        alpha = 0


        if 'input_0' in expr_list:
            input_0, tau, alpha = self.recursively_assemble_network(tau, alpha, input_image_variable,
                                                        input_text_attention_variable, expr_list['input_0'])
        if 'input_1' in expr_list:
            input_1, tau, alpha = self.recursively_assemble_network(tau, alpha, input_image_variable,
                                                        input_text_attention_variable, expr_list['input_1'])

        res, tau, alpha = current_module(tau, alpha, input_image_variable, text_at_time, input_0, input_1)
        return res, tau, alpha


    def forward(self, input_image_variable, input_text_attention_variable, target_answer_variable, expr_list):


        ##for now assume batch_size = 1
        result, tau, alpha = self.recursively_assemble_network(input_image_variable, input_text_attention_variable, expr_list)

        return result, tau, alpha


