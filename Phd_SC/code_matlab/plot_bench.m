close all
for ii=[1,3,4]
    figure
    jj=0;
for nl_lev=1:2
for nswp=1:2
jj=jj+1;
% ii=3;
omg=O(nswp,nl_lev,ii,:);
Ti=IT(nswp,nl_lev,ii,:);
omg=omg(omg~=0);
Ti=Ti(Ti~=0);
plot(omg(:),Ti(:),'o-.','Linewidth',2)
hold on
legend_str{jj}=[smoother_kinds{ii},' \upsilon=',num2str(nswp),' n_l=',num2str(4-nl_lev)];
end
end
legend(legend_str,'Location','Best')
grid on
xlabel \omega
ylabel('IT')
print(['Iterations_',strrep(smoother_kinds{ii},' ','_')],'-depsc')
savefig(['Iterations_',strrep(smoother_kinds{ii},' ','_')])
end
close all
for ii=[1,3,4]
    figure
    jj=0;
for nl_lev=1:2
for nswp=1:2
jj=jj+1;
% ii=3;
omg=O(nswp,nl_lev,ii,:);
Ti=t_totIT(nswp,nl_lev,ii,:);
omg=omg(omg~=0);
Ti=Ti(Ti~=0);
plot(omg(:),Ti(:),'o-.','Linewidth',2)
hold on
legend_str{jj}=[smoother_kinds{ii},' \upsilon=',num2str(nswp),' n_l=',num2str(4-nl_lev)];
end
end
legend(legend_str,'Location','Best')
grid on
xlabel \omega
ylabel('T_{tot} [s]')
print(['cputime_',strrep(smoother_kinds{ii},' ','_')],'-depsc')
savefig(['cputime_',strrep(smoother_kinds{ii},' ','_')])
end
close all
for ii=[1,3,4]
    figure
    jj=0;
for nl_lev=1:2
for nswp=1:2
jj=jj+1;
% ii=3;
omg=O(nswp,nl_lev,ii,:);
Ti=Final_res(nswp,nl_lev,ii,:);
omg=omg(omg~=0);
Ti=Ti(Ti~=0);
plot(omg(:),Ti(:),'o-.','Linewidth',2)
hold on
legend_str{jj}=[smoother_kinds{ii},' \upsilon=',num2str(nswp),' n_l=',num2str(4-nl_lev)];
end
end
legend(legend_str,'Location','Best')
grid on
xlabel \omega
ylabel('r_r')
print(['relres_',strrep(smoother_kinds{ii},' ','_')],'-depsc')
savefig(['relres_',strrep(smoother_kinds{ii},' ','_')])
end
close all
for ii=[1,3,4]
    figure
    jj=0;
for nl_lev=1:2
for nswp=1:2
jj=jj+1;
% ii=3;
omg=O(nswp,nl_lev,ii,:);
Ti=abbattimento_per_secondo(nswp,nl_lev,ii,:);
omg=omg(omg~=0);
Ti=Ti(Ti~=0);
Ti=Ti(Ti~=Inf);
Ti=Ti(Ti~=-Inf);
plot(omg(:),Ti(:),'o-.','Linewidth',2)
hold on
legend_str{jj}=[smoother_kinds{ii},' \upsilon=',num2str(nswp),' n_l=',num2str(4-nl_lev)];
end
end
legend(legend_str,'Location','Best')
grid on
xlabel \omega
ylabel('C_S [Hz]')
print(['convergence_speed_',strrep(smoother_kinds{ii},' ','_')],'-depsc')
savefig(['convergence_speed_',strrep(smoother_kinds{ii},' ','_')])
end
for ii=[1,3,4]
    figure
    jj=0;
for nl_lev=1:2
for nswp=1:2
jj=jj+1;
% ii=3;
omg=O(nswp,nl_lev,ii,:);
Ti=Abbattimento_specifico(nswp,nl_lev,ii,:);
omg=omg(omg~=0);
Ti=Ti(Ti~=0);
Ti=Ti(Ti~=Inf);
Ti=Ti(Ti~=-Inf);
plot(omg(:),Ti(:),'o-.','Linewidth',2)
hold on
legend_str{jj}=[smoother_kinds{ii},' \upsilon=',num2str(nswp),' n_l=',num2str(4-nl_lev)];
end
end
legend(legend_str,'Location','Best')
grid on
xlabel \omega
ylabel('ARR')
print(['ARR_',strrep(smoother_kinds{ii},' ','_')],'-depsc')
savefig(['ARR_',strrep(smoother_kinds{ii},' ','_')])
end