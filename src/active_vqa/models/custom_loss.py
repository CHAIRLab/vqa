import torch
import torch.nn as nn

class custom_loss(nn.Module):
    def __init__(self,lambda_entropy):
        super(custom_loss, self).__init__()
        self.lambda_entropy = lambda_entropy

    def forward(self, neg_entropy, answer_loss, policy_gradient_losses=None, layout_loss =None, tau_loss=None, alpha_loss=None, gamma = 0.5):
        answer = torch.mean(answer_loss)
        #entropy = torch.mean(neg_entropy)
        #policy_gradient = torch.mean(policy_gradient_losses)
        #print(" answer= %f, entropy  = %f, policy_gradient = %f" %
        #          (answer,entropy,policy_gradient))
        if tau_loss is None and alpha_loss is None:
            tau_alpha_loss = 0
        else:
            tau_alpha_loss = (1 - gamma) * tau_loss + gamma * alpha_loss

        if layout_loss is None:
            return tau_alpha_loss + torch.mean(neg_entropy) * self.lambda_entropy +\
               torch.mean(answer_loss)+torch.mean(policy_gradient_losses), answer
        else:
            return tau_alpha_loss + answer + layout_loss, answer
