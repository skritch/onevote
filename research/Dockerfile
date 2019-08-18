FROM jupyter/minimal-notebook

USER $NB_UID

COPY requirements.txt /opt/app/requirements.txt

RUN conda install ipython numpy pandas scikit-learn matplotlib seaborn && \
    conda install -c conda-forge jupyter_nbextensions_configurator && \
    conda clean --all -f -y && \
    fix-permissions $CONDA_DIR && \
    fix-permissions /home/$NB_USER

# Import matplotlib the first time to build the font cache.
ENV XDG_CACHE_HOME /home/$NB_USER/.cache/
RUN MPLBACKEND=Agg python -c "import matplotlib.pyplot" && \
    fix-permissions /home/$NB_USER

USER $NB_UID

RUN ipython3 profile create && \
    jupyter nbextensions_configurator enable --user

COPY jupyter_notebook_config.py /etc/jupyter/
COPY ipython_config.py /etc/ipython/profile_default/

ENTRYPOINT ["jupyter", "notebook", "--ip=0.0.0.0", "--no-browser", "--NotebookApp.token=''", "--allow-root"]
