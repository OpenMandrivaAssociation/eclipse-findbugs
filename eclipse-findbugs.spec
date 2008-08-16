%define eclipse_base    %{_libdir}/eclipse
%define fb_ver          1.3.4
%define fb_date         20080506
%define eclipse_ver     3.4
%define gcj_support     0

Name:           eclipse-findbugs
Version:        %{fb_ver}.%{fb_date}
Release:        %mkrel 1.1.9
Epoch:          0
Summary:        FindBugs Eclipse plugin
License:        LGPL
Group:          Development/Java
URL:            http://findbugs.sourceforge.net/
Source0:        http://heanet.dl.sourceforge.net/sourceforge/findbugs/eclipsePlugin-%{version}-source.zip
Source1:        %{name}-feature.xml
Patch0:         %{name}-build-xml.patch
Patch1:         %{name}-plugin-xml.patch
Requires:       eclipse-platform >= 1:%{eclipse_ver}
Requires:       findbugs = 0:%{fb_ver}
BuildRequires:  java-rpmbuild >= 0:1.5
BuildRequires:  ant >= 0:1.6
BuildRequires:  eclipse-pde >= 1:%{eclipse_ver}
BuildRequires:  findbugs = 0:%{fb_ver}
%if %{gcj_support}
BuildRequires:  java-gcj-compat-devel
%else
BuildRequires:  java-devel
BuildArch:      noarch
%endif
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root

%description
The FindBugs Eclipse plugin allows FindBugs to be used within the Eclipse IDE.

%prep
%setup -q -n eclipsePlugin-%{version}
%{__perl} -pi -e 's/<javac/<javac nowarn="true"/g' build.xml
%{__perl} -pi -e 's/fork="true"/fork="false"/' build.xml
%{__perl} -pi -e 's/date\)/"%{fb_date}")/' buildtools/de/tobject/findbugs/tools/PluginInfo.java
%{__perl} -pi -e 's/\r$//g' RELEASENOTES doc/*.txt
%{_bindir}/find . -name '*.jar' -o -name '*.zip' -o -name '*.class' | %{_bindir}/xargs -t %{__rm}
%patch0 -p1
#patch1 -p1

%build
export CLASSPATH=$(%{_bindir}/build-classpath findbugs bcel5.3 dom4j jaxen)

for jar in \
%{_libdir}/java/swt.jar \
%{eclipse_base}/plugins/org.eclipse.ant.core*.jar \
%{eclipse_base}/plugins/org.eclipse.ui.navigator*.jar \
%{eclipse_base}/plugins/org.eclipse.team.ui*.jar \
%{eclipse_base}/plugins/org.eclipse.compare*.jar \
%{eclipse_base}/plugins/org.eclipse.core.commands_%{eclipse_ver}*.*.jar \
%{eclipse_base}/plugins/org.eclipse.core.filebuffers_%{eclipse_ver}*.*.jar \
%{eclipse_base}/plugins/org.eclipse.core.resources_%{eclipse_ver}*.*.jar \
%{eclipse_base}/plugins/org.eclipse.core.runtime_%{eclipse_ver}*.*.jar \
%{eclipse_base}/dropins/jdt/plugins/org.eclipse.jdt.core_%{eclipse_ver}*.*.jar \
%{eclipse_base}/dropins/jdt/plugins/org.eclipse.jdt.ui_%{eclipse_ver}*.*.jar \
%{eclipse_base}/plugins/org.eclipse.jface_%{eclipse_ver}*.*.jar \
%{eclipse_base}/plugins/org.eclipse.jface.text_%{eclipse_ver}*.*.jar \
%{eclipse_base}/plugins/org.eclipse.osgi_%{eclipse_ver}*.*.jar \
%{eclipse_base}/plugins/org.eclipse.swt_%{eclipse_ver}*.*.jar \
%{eclipse_base}/plugins/org.eclipse.team.core_%{eclipse_ver}*.*.jar \
%{eclipse_base}/plugins/org.eclipse.text_%{eclipse_ver}*.*.jar \
%{eclipse_base}/plugins/org.eclipse.ui_%{eclipse_ver}*.*.jar \
%{eclipse_base}/plugins/org.eclipse.ui.editors_%{eclipse_ver}*.*.jar \
%{eclipse_base}/plugins/org.eclipse.ui.ide_%{eclipse_ver}*.*.jar \
%{eclipse_base}/plugins/org.eclipse.ui.workbench_%{eclipse_ver}*.*.jar \
%{eclipse_base}/plugins/org.eclipse.ui.workbench.texteditor_%{eclipse_ver}*.*.jar \
%{eclipse_base}/plugins/org.eclipse.equinox.common_%{eclipse_ver}*.*.jar \
%{eclipse_base}/plugins/org.eclipse.equinox.registry_%{eclipse_ver}*.*.jar \
%{eclipse_base}/plugins/org.eclipse.core.jobs_%{eclipse_ver}*.*.jar \
%{eclipse_base}/dropins/jdt/plugins/org.eclipse.jdt.launching_%{eclipse_ver}*.*.jar
do
    test -f  ${jar} || exit 1
    export CLASSPATH=$CLASSPATH:${jar}
done

export CLASSPATH=$CLASSPATH:`pwd`/bin_build
export OPT_JAR_LIST=:

%{ant} -Dbuild.sysclasspath=only \
    -Dfindbugs.dir=%{_javadir}/findbugs \
    -Declipse.plugin.dir=%{eclipse_base}/plugins \
    -Dworkspace=.. \
    -Declipse.version=%{eclipse_ver} \
    -Dproject.name="FindBugs Plug-in" \
    dist

%install
%{__rm} -rf %{buildroot}

%{__mkdir_p} %{buildroot}/%{eclipse_base}/features
%{__cp} -a %{SOURCE1} %{buildroot}/%{eclipse_base}/features/feature.xml

%{__mkdir_p} %{buildroot}/%{eclipse_base}/plugins
%{__unzip} bin_build/edu.umd.cs.findbugs.plugin.eclipse_%{version}.zip -d %{buildroot}/%{eclipse_base}/plugins
%{__cp} -a dist/* %{buildroot}/%{eclipse_base}/plugins/edu.umd.cs.findbugs.plugin.eclipse_%{version}

%{_bindir}/build-jar-repository \
    %{buildroot}/%{eclipse_base}/plugins/edu.umd.cs.findbugs.plugin.eclipse_%{version} \
    findbugs/annotations \
    asm3/asm3 \
    asm3/asm3-tree \
    bcel5.3 \
    dom4j \
    jaxen \
    findbugs/findbugs

%{_bindir}/build-jar-repository \
    %{buildroot}/%{eclipse_base}/plugins/edu.umd.cs.findbugs.plugin.eclipse_%{version}/plugin \
    findbugs/plugin/coreplugin

%{gcj_compile}

%clean 
%{__rm} -rf %{buildroot}

%if %{gcj_support}
%post
%{update_gcjdb}

%postun
%{clean_gcjdb}
%endif

%files
%defattr(0644,root,root,0755)
%doc doc/*.txt
%{eclipse_base}/features/*
%{eclipse_base}/plugins/*
%{gcj_files}
