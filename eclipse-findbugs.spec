%define eclipse_base    %{_datadir}/eclipse
%define fb_ver          1.2.1
%define fb_date         20070531
%define eclipse_ver     3.2
%define gcj_support     1

Name:           eclipse-findbugs
Version:        1.2.1.%{fb_date}
Release:        %mkrel 1.1.1
Epoch:          0
Summary:        FindBugs plugin for Eclipse
License:        LGPL
Group:          Development/Java
URL:            http://findbugs.sourceforge.net/
Source0:        http://heanet.dl.sourceforge.net/sourceforge/findbugs/eclipsePlugin-%{version}-source.zip
Patch0:         %{name}-jars.patch
Requires:       eclipse-platform >= 1:%{eclipse_ver}
Requires:       findbugs = 0:%{fb_ver}
BuildRequires:  jpackage-utils >= 0:1.5
BuildRequires:  ant >= 0:1.6
BuildRequires:  eclipse-pde >= 1:%{eclipse_ver}
BuildRequires:  findbugs = 0:%{fb_ver}
%if %{gcj_support}
BuildRequires:  java-gcj-compat-devel
Requires(post): java-gcj-compat
Requires(postun): java-gcj-compat
%else
BuildRequires:  java-devel
BuildArch:      noarch
%endif
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root

%description
The Eclipse FindBugs plugin integrates the FindBugs Java code
auditor into the Eclipse IDE. The plugin provides real-time feedback
to the user about violations of rules that check for coding style and
possible error prone code constructs. 

%prep
%setup -q -n eclipsePlugin-%{version}
%{__perl} -pi -e 's/<javac/<javac nowarn="true"/g' build.xml
%{__perl} -pi -e 's/fork="true"/fork="false"/' build.xml
%{__perl} -pi -e 's/date\)/"%{fb_date}")/' buildtools/de/tobject/findbugs/tools/PluginInfo.java
%{__perl} -pi -e 's/\r$//g' RELEASENOTES doc/*.txt
%{_bindir}/find . -name '*.jar' -o -name '*.zip' -o -name '*.class' | %{_bindir}/xargs -t %{__rm}
%patch0 -p1 -b .orig

%build
export CLASSPATH=$(%{_bindir}/build-classpath findbugs bcel5.3 dom4j jaxen)

for jar in \
%{_jnidir}/swt-gtk-%{eclipse_ver}*.jar \
%{eclipse_base}/plugins/org.eclipse.core.commands_%{eclipse_ver}*.*.jar \
%{eclipse_base}/plugins/org.eclipse.core.filebuffers_%{eclipse_ver}*.*.jar \
%{eclipse_base}/plugins/org.eclipse.core.resources_%{eclipse_ver}*.*.jar \
%{eclipse_base}/plugins/org.eclipse.core.runtime_%{eclipse_ver}*.*.jar \
%{eclipse_base}/plugins/org.eclipse.jdt.core_%{eclipse_ver}*.*.jar \
%{eclipse_base}/plugins/org.eclipse.jdt.ui_%{eclipse_ver}*.*.jar \
%{eclipse_base}/plugins/org.eclipse.jface_%{eclipse_ver}*.*.jar \
%{eclipse_base}/plugins/org.eclipse.jface.text_%{eclipse_ver}*.*.jar \
%{eclipse_base}/plugins/org.eclipse.osgi_%{eclipse_ver}*.*.jar \
%{eclipse_base}/plugins/org.eclipse.swt_%{eclipse_ver}*.*.jar \
%{eclipse_base}/plugins/org.eclipse.team.core_%{eclipse_ver}*.*.jar \
%{eclipse_base}/plugins/org.eclipse.team.cvs.core_%{eclipse_ver}*.*.jar \
%{eclipse_base}/plugins/org.eclipse.text_%{eclipse_ver}*.*.jar \
%{eclipse_base}/plugins/org.eclipse.ui_%{eclipse_ver}*.*.jar \
%{eclipse_base}/plugins/org.eclipse.ui.editors_%{eclipse_ver}*.*.jar \
%{eclipse_base}/plugins/org.eclipse.ui.ide_%{eclipse_ver}*.*.jar \
%{eclipse_base}/plugins/org.eclipse.ui.workbench_%{eclipse_ver}*.*.jar \
%{eclipse_base}/plugins/org.eclipse.ui.workbench.texteditor_%{eclipse_ver}*.*.jar \
%{eclipse_base}/plugins/org.eclipse.equinox.common_%{eclipse_ver}*.*.jar \
%{eclipse_base}/plugins/org.eclipse.equinox.registry_%{eclipse_ver}*.*.jar \
%{eclipse_base}/plugins/org.eclipse.core.jobs_%{eclipse_ver}*.*.jar \
%{eclipse_base}/plugins/org.eclipse.jdt.launching_%{eclipse_ver}*.*.jar
do
  test -f  ${jar} || exit 1
  export CLASSPATH=$CLASSPATH:${jar}
done

export CLASSPATH=$CLASSPATH:`pwd`/bin/classes

%{ant} -Dbuild.sysclasspath=only \
    -Dfindbugs.dir=%{_javadir}/findbugs \
    -Declipse.plugin.dir=%{eclipse_base}/plugins \
    -Dworkspace=.. \
    -Declipse.version=%{eclipse_ver} \
    -Dproject.name="FindBugs Plug-in" \
    dist

%install
%{__rm} -rf %{buildroot}

#%{__mkdir_p} %{buildroot}/%{eclipse_base}/features
%{__mkdir_p} %{buildroot}/%{eclipse_base}/plugins

%{__unzip} bin/edu.umd.cs.findbugs.plugin.eclipse_%{version}.zip -d %{buildroot}/%{eclipse_base}/plugins

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

%if %{gcj_support}
%{_bindir}/aot-compile-rpm
%endif

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
#%{eclipse_base}/features/*
%{eclipse_base}/plugins/*
%if %{gcj_support}
%dir %{_libdir}/gcj/%{name}
%attr(-,root,root) %{_libdir}/gcj/%{name}/*
%endif